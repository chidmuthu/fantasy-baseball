import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Bid


class BiddingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle WebSocket connection"""
        # Accept the connection
        await self.accept()
        
        # Join the bidding room
        await self.channel_layer.group_add(
            "bidding_updates",
            self.channel_name
        )
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave the bidding room
        await self.channel_layer.group_discard(
            "bidding_updates",
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'join_bid':
                bid_id = data.get('bid_id')
                if bid_id:
                    await self.channel_layer.group_add(
                        f"bid_{bid_id}",
                        self.channel_name
                    )
            
            elif message_type == 'leave_bid':
                bid_id = data.get('bid_id')
                if bid_id:
                    await self.channel_layer.group_discard(
                        f"bid_{bid_id}",
                        self.channel_name
                    )
        
        except json.JSONDecodeError:
            pass
    
    async def bid_update(self, event):
        """Send bid update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'bid_update',
            'bid_id': event['bid_id'],
            'data': event['data']
        }))
    
    async def bid_completed(self, event):
        """Send bid completion notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'bid_completed',
            'bid_id': event['bid_id'],
            'data': event['data']
        }))
    
    async def new_bid(self, event):
        """Send new bid notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'new_bid',
            'data': event['data']
        }))


class TeamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle WebSocket connection for team-specific updates"""
        # Accept the connection
        await self.accept()
        
        # Get user from scope
        user = self.scope.get('user')
        if user and not isinstance(user, AnonymousUser):
            # Join team-specific room
            team_id = await self.get_team_id(user)
            if team_id:
                await self.channel_layer.group_add(
                    f"team_{team_id}",
                    self.channel_name
                )
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        user = self.scope.get('user')
        if user and not isinstance(user, AnonymousUser):
            team_id = await self.get_team_id(user)
            if team_id:
                await self.channel_layer.group_discard(
                    f"team_{team_id}",
                    self.channel_name
                )
    
    @database_sync_to_async
    def get_team_id(self, user):
        """Get team ID for user"""
        try:
            return user.team.id
        except:
            return None
    
    async def team_update(self, event):
        """Send team update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'team_update',
            'data': event['data']
        }))
    
    async def prospect_acquired(self, event):
        """Send prospect acquisition notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'prospect_acquired',
            'data': event['data']
        })) 