#TODO Jihyun's code
#원래 코드는 openpose를 실행해서 나온 좌표를 csv에 저장하고 그 csv를 읽
import csv

def numericalization():

    key_point_csv = open('key_point_coordinates.csv','r')

    key_point = []
    key_point_raw = []

    for line in key_point_csv:
        key_point_raw.append(line.strip('\n'))

    for i in range(0, len(key_point_raw)):
        key_point.append(key_point_raw[i].split(','))

    for i in range(0, len(key_point)):
        for j in range(0, len(key_point[i])):
            key_point[i][j] = int(key_point[i][j].strip())

    pose_value = 0
            
    #몸의 방향
    #두 어깨의 x좌표 기준으로 측정
    left_shoulder_x = key_point[2][0]
    right_shoulder_x = key_point[5][0]

    if(left_shoulder_x == 0):
        pose_value += 1<<16 #01 우측 주시
    elif(right_shoulder_x == 0):
        pose_value += 1<<17 #10 좌측 주시
    elif(left_shoulder_x > right_shoulder_x):
        pose_value += 1<<17 
        pose_value += 1<<16 #11 뒤쪽 주시
    #else: 00, 정면 주시
            
    # detection안된 포인트들 채워주기
    if key_point[2][0] == 0 and key_point[2][1] == 0:
        key_point[2][0] = key_point[5][0]
        key_point[2][1] = key_point[5][1]
    if key_point[5][0] == 0 and key_point[5][1] == 0:
        key_point[5][0] = key_point[2][0]
        key_point[5][1] = key_point[2][1]
    
    if key_point[4][0] == 0 and key_point[4][1] == 0:
        key_point[4][0] = (key_point[2][0] + key_point[5][0])/2
        key_point[4][1] = (key_point[2][1] + key_point[5][1])/2
    if key_point[7][0] == 0 and key_point[7][1] == 0:
        key_point[7][0] = (key_point[2][0] + key_point[5][0])/2
        key_point[7][1] = (key_point[2][1] + key_point[5][1])/2
    
    if key_point[8][0] == 0 and key_point[8][1] == 0:
        key_point[8][0] = key_point[11][0]
        key_point[8][1] = key_point[11][1]
    if key_point[11][0] == 0 and key_point[11][1] == 0:
        key_point[11][0] = key_point[8][0]
        key_point[11][1] = key_point[8][1]
        
    if key_point[10][0] == 0 and key_point[10][1] == 0:
        key_point[10][0] = key_point[9][0]
        key_point[10][1] = key_point[13][1]
    if key_point[13][0] == 0 and key_point[13][1] == 0:
        key_point[13][0] = key_point[12][0]
        key_point[13][1] = key_point[10][1]
    

    #몸 높이
    #어깨-골반, 골반-무릎&발 사이의 거리를 기준으로 측정
    shoulder_h = (key_point[2][1] + key_point[5][1])/2
    hip_h = (key_point[8][1] + key_point[11][1])/2
    knee_h = (key_point[9][1] + key_point[12][1] + key_point[10][1] + key_point[13][1])/4

    upper_body = (hip_h - shoulder_h)/9*10
    lower_body = (knee_h - hip_h)/8*10

    if(abs(shoulder_h - knee_h) < abs(key_point[2][0] - key_point[5][0])):
        pose_value += 1<<19 #10, 누움
        print(shoulder_h, knee_h, abs(key_point[2][0] - key_point[5][0]))
    elif(upper_body*5/4 > lower_body):
        pose_value += 1<<19
        pose_value += 1<<18 #11, 앉음
    elif(lower_body*2/5 > upper_body):
        pose_value += 1<<18 #01, 숙임
    #else: 00, 서있음

    #손 위치
    #좌우는 어깨 넓이의 2/3을 기준으로 범위 계산
    #상하는 어깨 넓이의 1/2을 기준으로 범위 계산
    shoulder_width = (right_shoulder_x - left_shoulder_x)*2/3
    shoulder_height = (right_shoulder_x - left_shoulder_x)/2

    left_shoulder_y = key_point[2][1]
    right_shoulder_y = key_point[5][1]

    left_hand_x = key_point[4][0]
    left_hand_y = key_point[4][1]
    right_hand_x = key_point[7][0]
    right_hand_y = key_point[7][1]

    #왼손 좌우 위치
    if(left_hand_x < (left_shoulder_x - shoulder_width)):
        pose_value += 1<<15 #10, 왼쪽
    elif(left_hand_x > (left_shoulder_x + shoulder_width)):
        pose_value += 1<<14 #01, 오른쪽
    #else: 00, 가운데

    #왼손 상하 위치
    if(left_hand_y < (left_shoulder_y - shoulder_height)):
        pose_value += 1<<13 #10, 위
    elif(left_hand_y > (left_shoulder_y + shoulder_height)):
        pose_value += 1<<12 #01, 아래
    #else: 00, 가운데

    #오른손 좌우 위치
    if(right_hand_x < (right_shoulder_x - shoulder_width)):
        pose_value += 1<<11 #10, 왼쪽
    elif(right_hand_x > (right_shoulder_x + shoulder_width)):
        pose_value += 1<<10 #01, 오른쪽
    #else: 00, 가운데

    #왼손 상하 위치
    if(right_hand_y < (right_shoulder_y - shoulder_height)):
        pose_value += 1<<9 #10, 위
    elif(right_hand_y > (right_shoulder_y + shoulder_height)):
        pose_value += 1<<8 #01, 아래
    #else: 00, 가운데


    #발 위치
    left_hip_x = key_point[8][0]
    left_hip_y = key_point[8][1]
    right_hip_x = key_point[11][0]
    right_hip_y = key_point[11][1]

    left_foot_x = key_point[10][0]
    left_foot_y = key_point[10][1]
    right_foot_x = key_point[13][0]
    right_foot_y = key_point[13][1]

    hip_width = right_hip_x - left_hip_x

    #왼발 좌우 위치
    if(left_foot_x < (left_hip_x - hip_width)):
        pose_value += 1<<7 #10, 왼쪽
    elif(left_foot_x > (left_hip_x + hip_width)):
        pose_value += 1<<6 #01, 오른쪽
    #else: 00, 가운데

    #왼발 상하 위치
    if(left_foot_y < (left_hip_y + hip_width)):
        pose_value += 1<<5 #10, 위
    elif(left_foot_y > (left_hip_y + 2*hip_width)):
        pose_value += 1<<4 #01, 아래
    #else: 00, 가운데

    #오른발 좌우 위치
    if(right_foot_x < (right_hip_x - hip_width)):
        pose_value += 1<<3 #10, 왼쪽
    elif(right_foot_x > (right_hip_x + hip_width)):
        pose_value += 1<<2 #01, 오른쪽
    #else: 00, 가운데

    #오른발 상하 위치
    if(right_foot_y < (right_hip_y + hip_width)):
        pose_value += 1<<1 #10, 위
    elif(right_foot_y > (right_hip_y + 2*hip_width)):
        pose_value += 1<<0 #01, 아래
    #else: 00, 가운데

    return pose_value
