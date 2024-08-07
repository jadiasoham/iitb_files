from rest_framework import serializers

# def validate_input(value):
#     """
#     To ensure only valid bucket names are passed.
#     """
#     raise NotImplementedError()
    

class BucketSerializer(serializers.Serializer):
    name = serializers.CharField(
        min_length= 3,
        max_length= 63,
        # validators= [validate_input]
    )
    created_on = serializers.DateTimeField()

class ObjectSerializer(serializers.Serializer):
    name = serializers.CharField()
    size = serializers.FloatField()
    last_mod = serializers.DateTimeField()
