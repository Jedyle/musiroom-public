from django.dispatch import Signal


friendship_request_created = Signal()
friendship_request_rejected = Signal()
friendship_request_canceled = Signal()
friendship_request_viewed = Signal()
# friendship_request_accepted = Signal(providing_args=['from_user', 'to_user'])
# friendship_removed = Signal(providing_args=['from_user', 'to_user'])
# follower_created = Signal(providing_args=['follower'])
# follower_removed = Signal(providing_args=['follower'])
# followee_created = Signal(providing_args=['followee'])
# followee_removed = Signal(providing_args=['followee'])
# following_created = Signal(providing_args=['following'])
# following_removed = Signal(providing_args=['following'])
# block_created = Signal(providing_args=['blocker'])
# block_removed = Signal(providing_args=['blocker'])

# django 4 update
friendship_request_accepted = Signal()
friendship_removed = Signal()
follower_created = Signal()
follower_removed = Signal()
followee_created = Signal()
followee_removed = Signal()
following_created = Signal()
following_removed = Signal()
block_created = Signal()
block_removed = Signal()
