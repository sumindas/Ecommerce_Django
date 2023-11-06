from django.db.models.signals import post_save
from django.dispatch import receiver
from user.models import CustomUser, Order, Notification

# Signal for user creation
@receiver(post_save, sender=CustomUser)
def user_created_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance,
            message="Welcome to our platform!",
            event_type="User Created"
        )

# Signal for order placement
@receiver(post_save, sender=Order)
def order_placed_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.user,
            message=f"New order placed: Order ID {instance.id}",
            event_type="Order Placed"
        )

# Signal for account updates
@receiver(post_save, sender=CustomUser)
def account_updated_notification(sender, instance, created, **kwargs):
    if not created:
        message = f"Account for user '{instance.full_name}' has been updated."
        Notification.objects.create(
            user=instance,
            message=message,
            event_type="Account Updated"
        )
