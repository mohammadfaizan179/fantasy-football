from league.models import Player

STH_WENT_WRONG_MSG = "Something went wrong"
BAD_REQUEST = "Bad Request"
PERMISSION_ERROR = "Permission Error"
POSITION_CHOICES = {choice_key: choice_value for choice_key, choice_value in Player.POSITION_CHOICES}
