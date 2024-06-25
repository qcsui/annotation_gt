import pstats

# 读取分析结果
p = pstats.Stats('profile_results.pstats')
p.sort_stats('tottime').print_stats(100)
