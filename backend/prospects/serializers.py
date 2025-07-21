from rest_framework import serializers
from .models import Prospect


class ProspectSerializer(serializers.ModelSerializer):
    team = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    is_available = serializers.ReadOnlyField()
    current_bid = serializers.SerializerMethodField()
    age = serializers.ReadOnlyField()  # Add age as a read-only field
    
    # Eligibility fields
    is_eligible = serializers.ReadOnlyField()
    eligibility_status = serializers.ReadOnlyField()
    can_be_tagged = serializers.ReadOnlyField()
    eligibility_threshold_ab = serializers.ReadOnlyField()
    eligibility_threshold_ip = serializers.ReadOnlyField()
    next_tag_cost = serializers.ReadOnlyField()
    last_tagged_by = serializers.SerializerMethodField()
    
    class Meta:
        model = Prospect
        fields = [
            'id', 'name', 'position', 'organization', 'date_of_birth', 'age', 'level', 'eta',
            'team', 'acquired_at', 'created_by', 'created_at', 'updated_at',
            'is_available', 'current_bid',
            # Eligibility fields
            'at_bats', 'innings_pitched', 'tags_applied', 'last_tagged_at', 'last_tagged_by',
            'is_eligible', 'eligibility_status', 'can_be_tagged',
            'eligibility_threshold_ab', 'eligibility_threshold_ip', 'next_tag_cost'
        ]
        read_only_fields = ['acquired_at', 'created_at', 'updated_at', 'age', 'last_tagged_at']
    
    def get_team(self, obj):
        if obj.team:
            # Return minimal team info to avoid circular reference
            return {
                'id': obj.team.id,
                'name': obj.team.name,
                'owner': obj.team.owner.username if obj.team.owner else None
            }
        return None
    
    def get_created_by(self, obj):
        # Return minimal team info to avoid circular reference
        return {
            'id': obj.created_by.id,
            'name': obj.created_by.name,
            'owner': obj.created_by.owner.username if obj.created_by.owner else None
        }
    
    def get_current_bid(self, obj):
        bid = obj.current_bid
        if bid:
            # Return minimal bid info to avoid circular reference
            return {
                'id': bid.id,
                'current_bid': bid.current_bid,
                'status': bid.status,
                'last_bid_time': bid.last_bid_time,
                'time_remaining': bid.time_remaining,
                'is_expired': bid.is_expired
            }
        return None
    
    def get_last_tagged_by(self, obj):
        if obj.last_tagged_by:
            return {
                'id': obj.last_tagged_by.id,
                'name': obj.last_tagged_by.name,
                'owner': obj.last_tagged_by.owner.username if obj.last_tagged_by.owner else None
            }
        return None


class ProspectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prospect
        fields = ['name', 'position', 'organization', 'date_of_birth', 'level', 'eta']
    
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user.team
        return super().create(validated_data)


class ProspectUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prospect
        fields = ['position', 'organization', 'level', 'eta']
    
    def validate(self, data):
        # Only allow updates if user owns the prospect or is admin
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if not request.user.is_staff and self.instance.team != request.user.team:
                raise serializers.ValidationError("You can only edit prospects on your team")
        return data


class ProspectTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prospect
        fields = ['team']
    
    def validate(self, data):
        # Only admins can transfer prospects
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if not request.user.is_staff:
                raise serializers.ValidationError("Only admins can transfer prospects")
        return data


class ProspectTagSerializer(serializers.Serializer):
    """Serializer for tagging a prospect"""
    
    def validate(self, data):
        prospect = self.context.get('prospect')
        team = self.context.get('request').user.team
        
        if not prospect.can_be_tagged:
            raise serializers.ValidationError("This prospect cannot be tagged")
        
        tag_cost = prospect.next_tag_cost
        if team.pom_balance < tag_cost:
            raise serializers.ValidationError(f"Your team does not have enough POM to tag this prospect (cost: {tag_cost} POM)")
        
        return data 