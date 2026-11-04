import os
import cv2
import requests
import time
from datetime import datetime
from pathlib import Path


class ChangeDetection:
    HOST = os.getenv(
        "DJANGO_HOST",
        "http://127.0.0.1:8000"
    )

    username = os.getenv("DJANGO_USERNAME", "admin")
    password = os.getenv("DJANGO_PASSWORD")

    token = ""
    title = ""
    text = ""

    def __init__(self, names):
        # 각 클래스의 이전 검출 상태를 저장
        # 0 = 미검출, 1 = 검출
        self.result_prev = [0 for _ in range(len(names))]

        # 동일 객체의 서버 재전송 대기시간
        self.cooldown_seconds = float(
            os.getenv("POST_COOLDOWN_SECONDS", "30")
        )

        if self.cooldown_seconds < 0:
            raise ValueError(
                "POST_COOLDOWN_SECONDS는 0 이상이어야 합니다."
            )

        # 클래스별 마지막 서버 전송 시각
        self.last_sent_time = [
            0.0 for _ in range(len(names))
        ]

        print(
            f"Server POST cooldown: "
            f"{self.cooldown_seconds:.0f} seconds"
        )

        if not self.password:
            raise RuntimeError(
                "DJANGO_PASSWORD 환경변수가 설정되지 않았습니다."
            )
        
        # Django 서버에서 Token 발급
        res = requests.post(
            self.HOST + "/api-token-auth/",
            data={
                "username": self.username,
                "password": self.password
            }
        )

        res.raise_for_status()

        self.token = res.json()["token"]

        print("Django token authentication success")

    def add(self, names, detected_current, save_dir, image):
        self.title = ""
        self.text = ""

        change_flag = 0
        current_time = time.monotonic()
        send_classes = []

        for i in range(len(self.result_prev)):
            # 이전에는 없었는데 현재 새로 나타난 객체
            if self.result_prev[i] == 0 and detected_current[i] == 1:

                elapsed = current_time - self.last_sent_time[i]

                # Cooldown 시간이 지난 객체만 서버 전송 대상
                if elapsed >= self.cooldown_seconds:
                    change_flag = 1
                    send_classes.append(i)

                    self.title = names[i]
                    self.text += names[i] + ", "
                else:
                    print(
                        f"POST skipped: {names[i]} "
                        f"(cooldown {elapsed:.1f}/"
                        f"{self.cooldown_seconds:.1f}s)"
                    )

        # 현재 상태를 다음 프레임 비교용으로 저장
        self.result_prev = detected_current[:]

        # 새로운 객체가 나타난 경우에만 서버 전송
        if change_flag == 1:
            self.send(save_dir, image)

            # 실제 전송 대상으로 선택된 클래스만 시간 갱신
            for i in send_classes:
                self.last_sent_time[i] = current_time

    def send(self, save_dir, image):
        now = datetime.now()
        today = datetime.now()

        save_path = (
            Path.cwd()
            / save_dir
            / "detected"
            / str(today.year)
            / str(today.month)
            / str(today.day)
        )

        save_path.mkdir(parents=True, exist_ok=True)

        file_name = "{}-{}-{}-{}.jpg".format(
            today.hour,
            today.minute,
            today.second,
            today.microsecond
        )

        full_path = save_path / file_name

        # 서버 전송용 이미지 크기 축소
        dst = cv2.resize(
            image,
            dsize=(320, 240),
            interpolation=cv2.INTER_AREA
        )

        cv2.imwrite(str(full_path), dst)

        headers = {
            "Authorization": "Token " + self.token,
            "Accept": "application/json"
        }

        data = {
            "author": 1,
            "title": self.title,
            "text": self.text,
            "created_date": now.isoformat(),
            "published_date": now.isoformat()
        }

        with open(full_path, "rb") as image_file:
            files = {
                "image": image_file
            }

            res = requests.post(
                self.HOST + "/api_root/Post/",
                data=data,
                files=files,
                headers=headers
            )

        print("POST:", res.status_code)
        print(res.text)