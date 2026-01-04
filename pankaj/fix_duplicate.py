# fix_duplicate.py
import os
import sys
import django

# Add your project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bisht.settings')  # Replace 'bisht' with your project name
django.setup()

# Now import your models
from pankaj.models import ConsultationBooking, Payment  # Replace 'pankaj' with your app name
from django.db import transaction

def fix_duplicate_payments():
    """Find and fix duplicate payments"""
    print("=== Starting duplicate payment fix ===")
    
    with transaction.atomic():
        # Get all bookings
        bookings = ConsultationBooking.objects.all()
        total_fixed = 0
        
        for booking in bookings:
            try:
                # Get all payments for this booking
                payments = Payment.objects.filter(booking=booking)
                
                if payments.count() > 1:
                    print(f"\nFound {payments.count()} payments for booking {booking.booking_id}")
                    print(f"Client: {booking.name}, Email: {booking.email}")
                    
                    # List all payments for this booking
                    print("Payments found:")
                    for i, payment in enumerate(payments, 1):
                        print(f"  {i}. Payment ID: {payment.payment_id}, Status: {payment.status}, "
                              f"Method: {payment.method}, Created: {payment.created_at}")
                    
                    # Determine which payment to keep
                    # Priority: success > pending > failed
                    payment_to_keep = None
                    
                    # First, try to find a successful payment
                    successful_payments = payments.filter(status='success')
                    if successful_payments.exists():
                        payment_to_keep = successful_payments.latest('created_at')
                        print(f"Keeping successful payment: {payment_to_keep.payment_id}")
                    
                    # If no successful payment, try pending
                    if not payment_to_keep:
                        pending_payments = payments.filter(status='pending')
                        if pending_payments.exists():
                            payment_to_keep = pending_payments.latest('created_at')
                            print(f"Keeping pending payment: {payment_to_keep.payment_id}")
                    
                    # If still no payment, keep the latest one
                    if not payment_to_keep:
                        payment_to_keep = payments.latest('created_at')
                        print(f"Keeping latest payment: {payment_to_keep.payment_id}")
                    
                    # Delete other payments
                    payments_to_delete = payments.exclude(pk=payment_to_keep.pk)
                    delete_count = payments_to_delete.count()
                    
                    for payment in payments_to_delete:
                        print(f"Deleting duplicate payment: {payment.payment_id}")
                        payment.delete()
                    
                    # Update booking with kept payment ID
                    booking.payment_id = payment_to_keep.payment_id
                    booking.save()
                    
                    print(f"✓ Fixed booking {booking.booking_id}: Kept {payment_to_keep.payment_id}, "
                          f"Deleted {delete_count} duplicates")
                    total_fixed += 1
                    
                # Also fix bookings with payment_id but no payment object
                elif booking.payment_id and payments.count() == 0:
                    print(f"\nBooking {booking.booking_id} has payment_id {booking.payment_id} but no payment object")
                    
                    # Try to find payment by payment_id
                    try:
                        payment = Payment.objects.get(payment_id=booking.payment_id)
                        print(f"Found payment: {payment.payment_id}, linking to booking")
                        payment.booking = booking
                        payment.save()
                        print(f"✓ Linked payment {payment.payment_id} to booking")
                        total_fixed += 1
                    except Payment.DoesNotExist:
                        # Create a new payment record
                        payment = Payment.objects.create(
                            booking=booking,
                            payment_id=booking.payment_id,
                            amount=booking.price,
                            method='cash',  # Default
                            status='pending'
                        )
                        print(f"Created new payment: {payment.payment_id} for booking")
                        total_fixed += 1
                        
            except Exception as e:
                print(f"Error processing booking {booking.booking_id}: {str(e)}")
                continue
    
    print(f"\n=== Duplicate payment fix completed! ===")
    print(f"Total bookings fixed: {total_fixed}")
    
    # Show summary
    print("\n=== Payment Summary ===")
    total_bookings = ConsultationBooking.objects.count()
    total_payments = Payment.objects.count()
    print(f"Total bookings: {total_bookings}")
    print(f"Total payments: {total_payments}")
    
    # Check for bookings without payments
    bookings_without_payments = ConsultationBooking.objects.filter(payment__isnull=True).count()
    print(f"Bookings without payments: {bookings_without_payments}")
    
    # Check for payments without bookings
    payments_without_bookings = Payment.objects.filter(booking__isnull=True).count()
    print(f"Payments without bookings: {payments_without_bookings}")
    
    if bookings_without_payments > 0 or payments_without_bookings > 0:
        print("\n⚠️  Issues found! Running cleanup...")
        cleanup_orphaned_records()

def cleanup_orphaned_records():
    """Clean up orphaned records"""
    print("\n=== Cleaning up orphaned records ===")
    
    # Find payments without bookings
    orphaned_payments = Payment.objects.filter(booking__isnull=True)
    print(f"Found {orphaned_payments.count()} orphaned payments")
    
    for payment in orphaned_payments:
        print(f"Deleting orphaned payment: {payment.payment_id}")
        payment.delete()
    
    # Find bookings with invalid payment references
    invalid_bookings = ConsultationBooking.objects.filter(payment_id__isnull=False).exclude(
        payment_id__in=Payment.objects.values_list('payment_id', flat=True)
    )
    print(f"Found {invalid_bookings.count()} bookings with invalid payment references")
    
    for booking in invalid_bookings:
        print(f"Clearing invalid payment_id from booking: {booking.booking_id}")
        booking.payment_id = None
        booking.save()

def verify_fix():
    """Verify that the fix was successful"""
    print("\n=== Verification ===")
    
    # Check for duplicates
    from django.db.models import Count
    duplicate_payments = Payment.objects.values('booking').annotate(
        count=Count('id')
    ).filter(count__gt=1)
    
    if duplicate_payments.exists():
        print("❌ Still found duplicate payments!")
        for item in duplicate_payments:
            booking_id = item['booking']
            count = item['count']
            print(f"  Booking ID {booking_id}: {count} payments")
    else:
        print("✅ No duplicate payments found!")
    
    # Check for consistency
    inconsistent_bookings = ConsultationBooking.objects.exclude(
        payment_id__in=Payment.objects.values_list('payment_id', flat=True)
    ).filter(payment_id__isnull=False)
    
    if inconsistent_bookings.exists():
        print("❌ Found bookings with payment_id not matching any payment")
        for booking in inconsistent_bookings:
            print(f"  Booking {booking.booking_id}: payment_id {booking.payment_id}")
    else:
        print("✅ All payment references are valid!")

if __name__ == '__main__':
    print("=== Payment Duplicate Fix Tool ===")
    print("1. Fixing duplicate payments...")
    fix_duplicate_payments()
    
    print("\n2. Verifying fix...")
    verify_fix()
    
    print("\n=== Process Complete ===")