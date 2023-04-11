from manim import *
from math import pi, cos, sin
import sys
import mpmath
from sympy import diff, symbols, lambdify

# Run the following command in the folder of this document: manim -pql main.py Graph


# Feel free to modify these parameters:
SPEED = 1  # 1 is realtime, 2 is recommended

# The function which describes the position of the moving object along the circle path with respect to time.
# Modify the expression after the colon:
FUNCTION = lambda x: x**2 - 7*x + 1


def moving_rate(rule_function):
    def rate(t: float) -> float:
        return rule_function(t)

    return rate


def is_constant(func):
    result = func(0)
    return all(func(x) == result for x in range(10))


get_max_val = lambda f: max([f(x) for x in range(12)])
get_min_val = lambda f: min([f(x) for x in range(12)])


def construct_graph(x_position, func, color_of_func, color_of_area, t):

    if is_constant(func) and func(0) < 0:
        min_y = func(0) - 2
        max_y = 0
    elif is_constant(func):
        min_y = 0
        max_y = func(0) + 2
    else:
        min_y = get_min_val(func)
        max_y = get_max_val(func)

    ax = Axes(
        x_range=[0, 10], y_range=[min_y, max_y, (max_y-min_y)/10],
        x_length=3, y_length=3,

        axis_config={"include_tip": False}
    ).move_to([x_position, 2, 0])

    graph = ax.plot(func, color=color_of_func)

    dot = always_redraw(
        lambda: Dot(
            point=[ax.c2p(t.get_value(), func(t.get_value()))],
            color=color_of_func
        )
    )

    area = always_redraw(
        lambda: ax.get_area(
            graph,
            x_range=(0, t.get_value()),
            color=color_of_area,
            opacity=0.5,
        )
    )

    return ax, graph, dot, area


class CirclePlane:
    def __init__(self, r, color):
        self.radius = r
        self.circumference = 2 * r * pi

        self.circle = Circle(radius=r, color=color).set_y(-1.5)


class RotationalMotion:
    def __init__(self, plane, s_func):
        x = symbols('x')
        expr_of_s_func = s_func(x)

        self.plane = plane

        self.expr_of_distance_travelled = expr_of_s_func
        self.expr_of_speed = diff(expr_of_s_func, x)
        self.expr_of_acceleration = diff(self.expr_of_speed)

        self.func_of_distance_travelled = s_func
        self.func_of_speed = lambdify(x, diff(expr_of_s_func, x))

        if is_constant(self.func_of_speed):
            self.func_of_acceleration = lambda x: x
        else:
            self.func_of_acceleration = lambdify(x, diff(self.expr_of_speed))

        self.func_of_angle_travelled = lambda x: self.func_of_distance_travelled(x) / plane.radius

    def compute_rotating_point(self, t):
        x = self.plane.radius * cos(self.func_of_angle_travelled(t))
        y = self.plane.radius * sin(self.func_of_angle_travelled(t))
        return [self.plane.circle.get_center()[0] + x, self.plane.circle.get_center()[1] + y, 0]


plane = CirclePlane(2, WHITE)
situation = RotationalMotion(plane, FUNCTION)


class Graph(Scene):
    def construct(self):
        t = ValueTracker(0)

        ax1, graph1, dot1, area1 = construct_graph(-5, situation.func_of_distance_travelled, PINK, BLUE, t)
        ax2, graph2, dot2, area2 = construct_graph(0, situation.func_of_speed, BLUE, GREEN, t)
        ax3, graph3, dot3, area3 = construct_graph(5, situation.func_of_acceleration, GREEN, YELLOW, t)

        circle = plane.circle

        moving_object = always_redraw(lambda: Dot(point=situation.compute_rotating_point(t.get_value()), color=PINK))

        self.add(
            ax1, ax2, ax3,
            graph1, graph2, graph3,
            dot1, dot2, dot3,
            area1, area2, area3,
            circle, moving_object
        )

        self.play(t.animate.set_value(10), run_time=10*SPEED, rate_func=linear)

        self.wait(5)
