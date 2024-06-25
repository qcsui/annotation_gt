import random

import cProfile
import pstats
from line_profiler import LineProfiler

def generate_matrix(size):
    """生成一个指定大小的随机矩阵"""
    return [[random.random() for _ in range(size)] for _ in range(size)]

def matrix_multiply(A, B):
    """矩阵乘法"""
    size = len(A)
    result = [[0] * size for _ in range(size)]
    for i in range(size):
        for j in range(size):
            for k in range(size):
                result[i][j] += A[i][k] * B[k][j]
    # for i in range(size):
    #         print(result[i][0])
    return result


def main():
    for i in range(10):
        print(i)
        size = 100  # 定义矩阵大小
        A = generate_matrix(size)
        B = generate_matrix(size)
        result = matrix_multiply(A, B)
    return result

if __name__ == "__main__":


    # 创建一个LineProfiler对象
    profiler = LineProfiler()
    profiler.add_function(main)

    # 开始分析
    profiler.enable_by_count()
    main()
    profiler.disable_by_count()

    # 打印分析结果
    profiler.print_stats()
