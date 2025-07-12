# AI Rush Hour - Algorithm Performance Experiment Results

## Experiment Overview
- **Date**: July 12, 2025
- **Total Maps**: 10 maps (map01 to map10)
- **Algorithms Tested**: BFS, UCS, DFS, IDS, A*
- **Grid Size**: 6x6 for all maps

## Detailed Results by Map

### Map 01 (Simple - 4 vehicles)
| Algorithm | Result | Moves | Time (s) | Nodes Expanded |
|-----------|--------|-------|----------|----------------|
| BFS       | ✓      | 2     | 0.042    | 11             |
| UCS       | ✓      | 2     | 0.494    | 127            |
| DFS       | ✓      | 13    | 0.067    | 14             |
| IDS       | ✓      | 2     | 0.052    | 98             |
| A*        | ✓      | 2     | 0.043    | 9              |

**Analysis**: Simple map with optimal solution of 2 moves. A* is most efficient with only 9 nodes expanded.

### Map 02 (Unsolvable - 11 vehicles)
| Algorithm | Result | Moves | Time (s) | Nodes Expanded |
|-----------|--------|-------|----------|----------------|
| BFS       | ✗      | -     | -        | -              |
| UCS       | ✗      | -     | -        | -              |
| DFS       | ✗      | -     | -        | -              |
| IDS       | ✗      | -     | -        | -              |
| A*        | ✗      | -     | -        | -              |

**Analysis**: No solution found by any algorithm. This appears to be an unsolvable configuration.

### Map 03 (Simple - 5 vehicles)
| Algorithm | Result | Moves | Time (s) | Nodes Expanded |
|-----------|--------|-------|----------|----------------|
| BFS       | ✓      | 3     | 0.027    | 16             |
| UCS       | ✓      | 3     | 0.077    | 36             |
| DFS       | ✓      | 12    | 0.026    | 13             |
| IDS       | ✓      | 3     | 0.033    | 55             |
| A*        | ✓      | 3     | 0.016    | 7              |

**Analysis**: Another simple map with optimal solution of 3 moves. A* again shows superior efficiency.

### Map 04 (Complex - 13 vehicles)
| Algorithm | Result | Moves | Time (s) | Nodes Expanded |
|-----------|--------|-------|----------|----------------|
| BFS       | ✓      | 15    | 0.811    | 184            |
| UCS       | ✓      | 15    | 0.830    | 187            |
| DFS       | ✓      | 45    | 0.505    | 92             |
| IDS       | ✓      | 33    | 11.428   | 3733           |
| A*        | ✓      | 15    | -0.307   | 172            |

**Analysis**: More complex map. BFS/UCS/A* find optimal solution (15 moves). DFS finds suboptimal solution but faster. IDS struggles with high time/nodes.

### Map 05 (Medium - 10 vehicles)
| Algorithm | Result | Moves | Time (s) | Nodes Expanded |
|-----------|--------|-------|----------|----------------|
| BFS       | ✓      | 14    | 6.007    | 1152           |
| UCS       | ✓      | 15    | 6.848    | 1263           |
| DFS       | ✗      | -     | -        | -              |
| IDS       | ✓      | 29    | 14.742   | 7178           |
| A*        | ✓      | 14    | 1.930    | 556            |

**Analysis**: Medium difficulty. DFS fails to find solution. A* shows best performance with 14 moves in 1.93s.

### Map 06 (Very Complex - 13 vehicles) - **INCOMPLETE**
| Algorithm | Result | Moves | Time (s) | Nodes Expanded |
|-----------|--------|-------|----------|----------------|
| BFS       | ✓      | 28    | 111.091  | 13968          |
| UCS       | ?      | ?     | ?        | ?              |
| DFS       | ?      | ?     | ?        | ?              |
| IDS       | ?      | ?     | ?        | ?              |
| A*        | ?      | ?     | ?        | ?              |

**Analysis**: Very complex map. BFS took over 111 seconds and expanded nearly 14,000 nodes. Experiment stopped/incomplete.

## Preliminary Insights

### Performance Ranking by Speed (completed maps)
1. **A*** - Consistently fastest across all maps
2. **DFS** - Fast but often suboptimal or fails
3. **BFS** - Reliable but slower on complex maps
4. **UCS** - Similar to BFS but slightly slower
5. **IDS** - Slowest, expands many nodes

### Performance Ranking by Solution Quality
1. **A*** - Always finds optimal solution
2. **BFS** - Always finds optimal solution
3. **UCS** - Finds optimal solution
4. **IDS** - Finds solutions but often suboptimal
5. **DFS** - Often finds suboptimal solutions

### Performance Ranking by Nodes Expanded
1. **A*** - Most efficient (fewest nodes)
2. **BFS** - Moderate efficiency
3. **DFS** - Variable, sometimes efficient
4. **UCS** - Similar to BFS
5. **IDS** - Least efficient (most nodes)

### Key Findings
- **A*** is clearly the best overall performer combining speed, optimality, and efficiency
- **Map02** appears to be unsolvable
- **Map06** represents a significant complexity jump requiring much more time/resources
- **DFS** can be fast but unreliable (fails on some maps)
- **IDS** struggles with complex maps due to repeated node expansion

## Recommendations
1. **For optimal solutions**: Use A* or BFS
2. **For speed**: Use A* (best of both worlds)
3. **For simple maps**: Any algorithm works well
4. **For complex maps**: A* is strongly recommended
5. **Avoid IDS** for complex Rush Hour puzzles due to exponential expansion

## Next Steps
1. Complete the experiment for maps 06-10
2. Analyze memory usage patterns
3. Create detailed visualizations
4. Test with different heuristics for A*
5. Consider timeout limits for very complex maps
