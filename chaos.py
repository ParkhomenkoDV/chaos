from math import atan2, cos, pi, sin
from random import randint, random
from typing import List, Tuple

import pygame

WIDTH, HEIGHT = 1_000, 1_000
FPS = 60
ENTROPHY = 10


balls: List["Ball"] = []


def distance(p1: Tuple[float, float], p2: Tuple[float, float]):
    """Расстояние между двумя точками"""
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5


def collisions() -> None:
    """Обработка всех упругих столкновений (сохранение импульса и энергии) между шарами"""
    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            ball1, ball2 = balls[i], balls[j]

            # Проверяем столкновение
            dx = ball2.x - ball1.x
            dy = ball2.y - ball1.y
            dist = (dx * dx + dy * dy) ** 0.5
            min_distance = ball1.radius + ball2.radius

            if dist < min_distance:
                # Нормализуем вектор расстояния
                if dist == 0:
                    # Шары в одной точке - немного раздвигаем
                    dx, dy = 1, 0
                    dist = 1

                nx = dx / dist  # Нормаль по X
                ny = dy / dist  # Нормаль по Y

                # Перемещаем шары так, чтобы они не пересекались
                overlap = min_distance - dist
                ball1.x -= overlap * nx * 0.5
                ball1.y -= overlap * ny * 0.5
                ball2.x += overlap * nx * 0.5
                ball2.y += overlap * ny * 0.5

                dvx = ball2.vx - ball1.vx
                dvy = ball2.vy - ball1.vy
                # Вычисляем проекцию относительной скорости на нормаль
                velocity_along_normal = dvx * nx + dvy * ny

                # Если шары удаляются друг от друга, не обрабатываем столкновение
                if velocity_along_normal > 0:
                    continue

                # Коэффициент восстановления (1 для абсолютно упругого)
                restitution = 1.0

                # Импульс столкновения
                impulse = 2 * velocity_along_normal / (ball1.m + ball2.m)

                # Проекции скоростей
                vx1 = ball1.vx + impulse * ball2.m * nx * restitution
                vy1 = ball1.vy + impulse * ball2.m * ny * restitution

                vx2 = ball2.vx - impulse * ball1.m * nx * restitution
                vy2 = ball2.vy - impulse * ball1.m * ny * restitution

                ball1.v = (vx1**2 + vy1**2) ** 0.5
                ball2.v = (vx2**2 + vy2**2) ** 0.5

                # 7. Обновляем скорость и угол для ball1
                ball1.v = (vx1**2 + vy1**2) ** 0.5
                ball1.angle = atan2(vy1, vx1)

                # 8. Обновляем скорость и угол для ball2
                ball2.v = (vx2**2 + vy2**2) ** 0.5
                ball2.angle = atan2(vy2, vx2)


class Ball:
    R_MIN, R_MAX = 2, min(WIDTH, HEIGHT) // 4
    V_MAX = FPS // 30  # 1 fps = 1 ppx per second // 2 as 2 balls

    ID = 0

    __slots__ = ("id", "radius", "color", "v", "angle", "x", "y")

    def __init__(
        self,
        radius: int = None,
        angle: float = None,
    ):
        self.id = Ball.ID
        Ball.ID += 1

        if isinstance(radius, int):
            assert Ball.R_MIN <= radius <= Ball.R_MAX, f"{radius=} not in [{Ball.R_MIN}..{Ball.R_MAX}]"
            self.radius = radius
        else:
            self.radius = randint(Ball.R_MIN, Ball.R_MAX)

        self.color = pygame.Color(randint(0, 255), randint(0, 255), randint(0, 255), randint(0, 255))

        self.v = random() * self.V_MAX

        if isinstance(angle, (int, float)):
            assert 0 <= angle <= 2 * pi, f"{angle=} not in [0..{2*pi=}]"
            self.angle = angle
        else:
            self.angle = random() * 2 * pi

        self.x = randint(self.radius, WIDTH - self.radius)
        self.y = randint(self.radius, HEIGHT - self.radius)

    @property
    def m(self) -> int | float:
        """Псевдомасса"""
        return self.radius**3  # 4/3 * pi * r**3

    @property
    def vx(self):
        return self.v * cos(self.angle)

    @property
    def vy(self):
        return self.v * sin(self.angle)

    @property
    def is_outside(self):
        """Выход за границы экрана"""
        return self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT

    def is_collide(self, ball) -> bool:
        """Столкнулся ли он c другим шаром"""
        return distance((self.x, self.y), (ball.x, ball.y)) <= self.radius + ball.radius

    def move(self) -> None:
        """Расчет новой координаты"""
        # следующая координата
        x = self.x + self.v * cos(self.angle)
        y = self.y + self.v * sin(self.angle)

        # столкновения со стенками
        if (x - self.radius < 0) and cos(self.angle) < 0:  # левая стенка
            self.angle = pi - self.angle
            x = self.x
        elif (x + self.radius > WIDTH) and cos(self.angle) > 0:  # правая стенка
            self.angle = pi - self.angle
            x = self.x
        if (y - self.radius < 0) and sin(self.angle) < 0:  # верхняя стенка
            self.angle = -self.angle
            y = self.y
        elif (y + self.radius > HEIGHT) and sin(self.angle) > 0:  # нижняя стенка
            self.angle = -self.angle
            y = self.y

        self.x, self.y = x, y

    def draw(self, window):
        """Рисование шара на экране"""
        pygame.draw.circle(window, self.color, (self.x, self.y), self.radius)
        pygame.draw.line(window, "black", (int(self.x), int(self.y)), (int(self.x + self.vx), int(self.y + self.vy)), 2)  # Вектор скорости


def main(entrophy: int):
    global balls

    pygame.init()
    pygame.display.set_caption("Chaos")
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    for _ in range(entrophy):
        while True:
            new_ball = Ball()
            for ball in balls:
                if new_ball.is_collide(ball):
                    break
            else:
                balls.append(new_ball)
                break

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        for ball in balls:
            ball.move()

        collisions()

        balls[:] = [ball for ball in balls if not ball.is_outside]  # Удаление шаров, вылетевших за пределы (на всякий случай)

        window.fill("white")
        for ball in balls:
            ball.draw(window)

        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main(ENTROPHY)
