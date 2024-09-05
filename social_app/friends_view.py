from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import FriendRequest
from .serializers import FriendRespondSerializer,FriendRequestSerializer,UserSerializer
from django.db.models import Q
from django.contrib.auth import get_user_model

User=get_user_model()


def can_send_friend_request(user):
    one_minute_ago = timezone.now() - timedelta(minutes=1)
    recent_requests = FriendRequest.objects.filter(sender=user, created_at__gte=one_minute_ago)
    return recent_requests.count() < 3

class SendFriendRequestView(generics.GenericAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if not can_send_friend_request(request.user):
            return Response({"detail": "You can send a maximum of 3 friend requests within a minute."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        receiver_id = request.data.get('receiver')
        print(request.data)
        try:
            receiver = User.objects.get(id=receiver_id)
            if receiver==request.user:
                return Response({"detail": "You can't send friend requet to yourself !"}, status=status.HTTP_400_BAD_REQUEST)
            if FriendRequest.objects.filter(sender=request.user, receiver=receiver,status='Accepted').exists():
                return Response({"detail": "You are friends already."}, status=status.HTTP_400_BAD_REQUEST)
            if FriendRequest.objects.filter(sender=request.user, receiver=receiver).exists():
                return Response({"detail": "Friend request already sent."}, status=status.HTTP_400_BAD_REQUEST)
            friend_request = FriendRequest.objects.create(sender=request.user, receiver=receiver)
            serializer=FriendRequestSerializer(friend_request)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({"detail": "Receiver not found."}, status=status.HTTP_404_NOT_FOUND)

class RespondFriendRequestView(generics.GenericAPIView):
    serializer_class = FriendRespondSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        print(request.data)
        friend_request_id = request.data.get('sender')
        print(friend_request_id)
        action = request.data.get('action') 
        try:
            friend_request = FriendRequest.objects.get(sender=friend_request_id, receiver=request.user)
            if friend_request.status != 'sent':
                return Response({"detail": "Action already taken on this request."}, status=status.HTTP_400_BAD_REQUEST)
            if action == 'accept':
                friend_request.status = 'accepted'
            elif action == 'reject':
                friend_request.status = 'rejected'
            else:
                return Response({"detail": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)
            friend_request.save()
            return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": e.__str__()}, status=status.HTTP_404_NOT_FOUND)

class ListFriendsView(generics.GenericAPIView):
    serializer_class = UserSerializer
    queryset = FriendRequest.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            accepted_requests = FriendRequest.objects.filter(
                Q(sender=request.user, status='accepted') | Q(receiver=request.user, status='accepted')
            )
            friend_ids = set()
            for friend_request in accepted_requests:
                if friend_request.sender != request.user:
                    friend_ids.add(friend_request.sender.id)
                if friend_request.receiver != request.user:
                    friend_ids.add(friend_request.receiver.id)
            friend_users = User.objects.filter(id__in=friend_ids).distinct()
            serializer = self.get_serializer(friend_users, many=True)
            return Response(data={"friends":serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error":e.__str__()},status=status.HTTP_200_OK)
        

class ListPendingRequestsView(generics.GenericAPIView):
    serializer_class = FriendRequestSerializer
    queryset=FriendRequest.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        try:
            pending_requests = FriendRequest.objects.filter(receiver=request.user, status="sent")
            serializer = self.get_serializer(pending_requests, many=True)
            return Response(data={"pending_friend_requests":serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error":e.__str__()},status=status.HTTP_200_OK)
