from django.db import models


class Choreo(models.Model):
    choreo_id = models.CharField(primary_key=True, max_length=30)
    download_url = models.URLField(max_length=150)
    start_sec = models.FloatField(default=0.00)
    end_sec = models.FloatField(default=0.00)

    def __str__(self):
        return self.choreo_id


class ChoreoSlice(models.Model):
    choreo_slice_id = models.CharField(primary_key=True, max_length=35)
    movement = models.CharField(max_length=130)
    duration = models.FloatField(default=-1.00)
    intro = models.BooleanField(default=False)
    outro = models.BooleanField(default=False)
    start_pose_type = models.CharField()
    end_pose_type = models.BinaryField(max_length=40)
    audio_slice_id = models.CharField(max_length=35)
    choreo_id = models.ForeignKey(Choreo, on_delete=models.CASCADE)

    def __str__(self):
        return self.choreo_slice_id
