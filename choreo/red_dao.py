from django.core.cache import cache
from django.core.cache import caches
import config
from choreo.models import ChoreoSlice

"""
REDIS CONNECTIONS
"""
user_redis = caches["default"]
progress_redis = caches["choreo-product"]

"""
choleor-audio container (page2)
"""
request_user_id = "a30gk3"
user_key = "user:" + request_user_id
user_dict = {
    "audio_id": "",
    "start_idx": 0,
    "end_idx": 20,
    "counter": 0
}
# after getting resp from rabbit mq, before respond to client
user_redis.hset(user_key, user_dict)

# after resp to client --> ASYNC + CELERY
ampl_redis = user_redis
ampl_key = "ampl:"
ampl_redis.rpush()
# preprocess

# after
smlr_redis = user_redis
smlr_key = "smlr:"
smlr_redis.rpush()
"""
choreo container
"""
client_audio_slice_id = "dkdki93k_3"
client_audio_idx = client_audio_slice_id.split("_")[1]
selected_choreo_idx = 0

pgrss_key = "pgrss" + request_user_id

# 마지막 choreography 인 경우
if user_redis.hget(user_key, "end_idx") == client_audio_idx:
    # rabbitmq or redis로 끝났다고 메시지 보내기 - 미리 만들게?
    user_redis.expire(user_key, 1)
    # 여기서 영상이랑 노래 볼륨 엑세스해서 합치는걸로

# 여기에 rabbitmq로부터 메시지 받았는지 확인
if user_redis.hget(user_key, "start_idx") == client_audio_idx:
    choreo_candidates = ChoreoSlice.objects.order_by('?')[:6]
    user_redis.hset(user_key, "counter", client_audio_idx)
    # 여기서 영상이랑 노래 볼륨 엑세스해서 합치는걸로 넘어가기
    # 가져와서 합치는 놈한테 넘길까..

# 앞으로 가서 다시 선택하는 경우 등 중간에 있는 부분
if user_redis.hget(user_key, "counter") <= client_audio_idx:
    progress_redis.ltrim("pgrss-" + user_key, client_audio_idx, -1)
# 현재 user 상황을 counter로 재설정
user_redis.hset(user_key, "counter", client_audio_idx)
# user가 오디오부분마다 선택한 choreography 프로그레스를 받은 choreo idx로 설정
progress_redis.rpush(pgrss_key, client_audio_idx, selected_choreo_idx)

# 해당 choreo_idx와 이어질 수 있는 pose를 가져와야 함 --> type XOR 연산
filter_res = ChoreoSlice.objects.values_list('start_pose_type', 'choreo_slice_id', 'audio_slice_id')
selected_pose_type = ChoreoSlice.objects.get(choreo_slice_id=selected_choreo_idx).end_pose_type
for i in filter_res:
    if i[0] ^ selected_pose_type >= 3:
        del i

# pose_type으로 필터된 choreo_slice_id, audio_slice_id
choreo_slice_candidates = [i[1] for i in filter_res]
audio_slice_candidates = [i[2] for i in filter_res]

# 2-a 노래 유사도
# smlr_res = reversed([smlr_redis.brpoplpush(smlr_key, smlr_key) for i in smlr_redis.llen(smlr_key)])
smlr_dict = {}  # {audio_slice_id : similarity_score}
for i in range(smlr_redis.llen(smlr_key)):
    item = smlr_redis.brpoplpush(smlr_key, smlr_key).split(":")
    if item[0] in audio_slice_candidates:
        smlr_dict[item[0]] = item[1]

# 2-b async랑 multiprocess 돌리자
# 2-b-1
ampl_res = reversed([ampl_redis.brpoplpush(ampl_key, ampl_key) for i in range(5)])
# 2-b-2
movement_res = [i[1] for i in ChoreoSlice.objects.values_list('choreo_slice_id', 'movement') if
                i[0] in choreo_slice_candidates]
