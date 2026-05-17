"""Dependency graph builder and cycle detector for element conditions."""

from app.services.condition_engine import ConditionEngine


class DependencyValidator:
    def __init__(self) -> None:
        self._engine = ConditionEngine()

    def build_dependency_graph(self, elements: list[dict]) -> dict[str, list[str]]:
        graph: dict[str, list[str]] = {e["key"]: [] for e in elements}

        for elem in elements:
            key = elem["key"]
            deps = self._extract_dependencies(elem)
            for dep in deps:
                if dep in graph:
                    if key not in graph[dep]:
                        graph[dep].append(key)
        return graph

    def detect_cycles(self, elements: list[dict]) -> list[str] | None:
        graph = self.build_dependency_graph(elements)
        visited: set[str] = set()
        in_stack: set[str] = set()
        path: list[str] = []

        for node in graph:
            cycle = self._dfs(node, graph, visited, in_stack, path)
            if cycle is not None:
                return cycle
        return None

    def get_stats(self, elements: list[dict]) -> dict:
        graph = self.build_dependency_graph(elements)
        dep_count = sum(len(deps) for deps in graph.values())
        max_depth = self._compute_max_depth(graph)
        return {"dependency_count": dep_count, "max_depth": max_depth}

    def _extract_dependencies(self, elem: dict) -> set[str]:
        deps: set[str] = set()
        for condition_key in ("visible_when", "required_when"):
            cond = elem.get(condition_key)
            if cond and isinstance(cond, dict):
                for c in cond.get("conditions", []):
                    field = c.get("field")
                    if field:
                        deps.add(field)

        computed = elem.get("computed_value")
        if computed:
            try:
                refs = self._engine.get_expression_references(computed)
                deps.update(refs)
            except (ValueError, SyntaxError):
                pass
        return deps

    def _dfs(
        self,
        node: str,
        graph: dict[str, list[str]],
        visited: set[str],
        in_stack: set[str],
        path: list[str],
    ) -> list[str] | None:
        if node in in_stack:
            cycle_start = path.index(node)
            return path[cycle_start:] + [node]
        if node in visited:
            return None

        visited.add(node)
        in_stack.add(node)
        path.append(node)

        for neighbor in graph.get(node, []):
            cycle = self._dfs(neighbor, graph, visited, in_stack, path)
            if cycle is not None:
                return cycle

        path.pop()
        in_stack.remove(node)
        return None

    def _compute_max_depth(self, graph: dict[str, list[str]]) -> int:
        memo: dict[str, int] = {}

        def depth(node: str, seen: set[str]) -> int:
            if node in memo:
                return memo[node]
            if node in seen:
                return 0
            seen.add(node)
            children = graph.get(node, [])
            if not children:
                memo[node] = 0
                return 0
            d = 1 + max(depth(c, seen) for c in children)
            memo[node] = d
            return d

        max_d = 0
        for n in graph:
            max_d = max(max_d, depth(n, set()))
        return max_d
