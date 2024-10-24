import enum


class OrderStatus(enum.Enum):
    processing = "Processing"
    processed = "Processed"
    Send_you = "Send you"
    delivered = "Delivered"
    received = "Received"
    cancelled = "Cancelled"
