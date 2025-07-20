from rest_framework import serializers
from .models import Bid, BidHistory
import logging

logger = logging.getLogger(__name__)


class BidHistorySerializer(serializers.ModelSerializer):
    team = serializers.SerializerMethodField()
    
    class Meta:
        model = BidHistory
        fields = ['id', 'team', 'amount', 'bid_time']
    
    def get_team(self, obj):
        from teams.serializers import TeamSerializer
        return TeamSerializer(obj.team, context=self.context).data


class BidSerializer(serializers.ModelSerializer):
    prospect = serializers.SerializerMethodField()
    nominator = serializers.SerializerMethodField()
    current_bidder = serializers.SerializerMethodField()
    time_remaining = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    history = BidHistorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Bid
        fields = [
            'id', 'prospect', 'nominator', 'current_bidder', 'starting_bid', 
            'current_bid', 'status', 'created_at', 'last_bid_time', 'completed_at',
            'expires_at', 'time_remaining', 'is_expired', 'history'
        ]
        read_only_fields = ['created_at', 'last_bid_time', 'completed_at', 'expires_at']
    
    def get_prospect(self, obj):
        from prospects.serializers import ProspectSerializer
        return ProspectSerializer(obj.prospect, context=self.context).data
    
    def get_nominator(self, obj):
        from teams.serializers import TeamSerializer
        return TeamSerializer(obj.nominator, context=self.context).data
    
    def get_current_bidder(self, obj):
        from teams.serializers import TeamSerializer
        return TeamSerializer(obj.current_bidder, context=self.context).data


class BidCreateSerializer(serializers.ModelSerializer):
    prospect_data = serializers.DictField(write_only=True)
    
    class Meta:
        model = Bid
        fields = ['starting_bid', 'prospect_data']
    
    def validate_starting_bid(self, value):
        if value < 5:
            raise serializers.ValidationError("Starting bid must be at least 5 POM")
        return value
    
    def validate(self, data):
        # Check if team can afford the starting bid (considering all active bids)
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            available_pom = request.user.team.get_available_pom()
            can_afford = request.user.team.can_afford_bid(data['starting_bid'])
            
            logger.info(f"Bid creation validation for team {request.user.team.name}:")
            logger.info(f"  - Current balance: {request.user.team.pom_balance} POM")
            logger.info(f"  - Available POM: {available_pom} POM")
            logger.info(f"  - Starting bid: {data['starting_bid']} POM")
            logger.info(f"  - Can afford: {can_afford}")
            
            if not can_afford:
                error_msg = (
                    f"Insufficient available POM. You have {available_pom} POM available "
                    f"(current balance: {request.user.team.pom_balance} POM, "
                    f"committed to other bids: {request.user.team.pom_balance - available_pom} POM)"
                )
                logger.warning(f"  - Validation failed: {error_msg}")
                raise serializers.ValidationError({
                    'non_field_errors': [error_msg]
                })
            
            logger.info(f"  - Validation passed")
        return data
    
    def create(self, validated_data):
        from prospects.models import Prospect
        
        prospect_data = validated_data.pop('prospect_data')
        request = self.context.get('request')
        
        # Create the prospect first
        prospect_data['created_by'] = request.user.team
        prospect = Prospect.objects.create(**prospect_data)
        
        # Create the bid
        bid = Bid.objects.create(
            prospect=prospect,
            nominator=request.user.team,
            current_bidder=request.user.team,
            starting_bid=validated_data['starting_bid'],
            current_bid=validated_data['starting_bid']
        )
        
        # Set initial expiration time
        bid.update_expiration_time()
        
        return bid


class BidPlaceSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=1)
    
    def validate_amount(self, value):
        bid = self.context.get('bid')
        if bid and value <= bid.current_bid:
            raise serializers.ValidationError(f"Bid must be higher than current bid of {bid.current_bid} POM")
        return value
    
    def validate(self, data):
        request = self.context.get('request')
        bid = self.context.get('bid')
        
        logger.info(f"BidPlaceSerializer.validate() called with data: {data}")
        
        if not request or not bid:
            logger.error("Invalid context - missing request or bid")
            raise serializers.ValidationError("Invalid context")
        
        # Check if bid is still active
        if bid.status != 'active':
            logger.warning(f"Bid {bid.id} is not active (status: {bid.status})")
            raise serializers.ValidationError("Cannot bid on inactive auction")
        
        # Check if team can afford the bid (considering all active bids)
        available_pom = request.user.team.get_available_pom(exclude_bid=bid)
        can_afford = request.user.team.can_afford_bid(data['amount'], exclude_bid=bid)
        
        logger.info(f"Bid validation for team {request.user.team.name}:")
        logger.info(f"  - Current balance: {request.user.team.pom_balance} POM")
        logger.info(f"  - Available POM: {available_pom} POM")
        logger.info(f"  - Bid amount: {data['amount']} POM")
        logger.info(f"  - Can afford: {can_afford}")
        
        if not can_afford:
            error_msg = (
                f"Insufficient available POM. You have {available_pom} POM available "
                f"(current balance: {request.user.team.pom_balance} POM, "
                f"committed to other bids: {request.user.team.pom_balance - available_pom} POM)"
            )
            logger.warning(f"  - Validation failed: {error_msg}")
            logger.warning(f"  - Raising ValidationError with non_field_errors")
            raise serializers.ValidationError({
                'non_field_errors': [error_msg]
            })
        
        logger.info(f"  - Validation passed")
        return data
    
    def save(self, **kwargs):
        request = self.context.get('request')
        bid = self.context.get('bid')
        
        logger.info(f"BidPlaceSerializer.save() called")
        logger.info(f"  - Team: {request.user.team.name}")
        logger.info(f"  - Amount: {self.validated_data['amount']}")
        logger.info(f"  - Bid ID: {bid.id}")
        
        try:
            bid.place_bid(request.user.team, self.validated_data['amount'])
            logger.info(f"  - place_bid() completed successfully")
            return bid
        except ValueError as e:
            logger.error(f"  - place_bid() failed with ValueError: {e}")
            raise serializers.ValidationError(str(e)) 