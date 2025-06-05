from collections import defaultdict

tree = {"홍익대학교": {}}

# tree_state.py
def update_tree(path, value):
    node = tree
    for key in path[:-1]:
        current = node.get(key)
        if not isinstance(current, dict):
            node[key] = {}
        node = node[key]

    leaf = path[-1]

    # ❗ leaf가 없으면 빈 dict 생성
    if leaf not in node:
        if value in [None, "", [], {}]:
            node[leaf] = {}  # 의도적 존재 표시
        else:
            node[leaf] = value
    else:
        existing = node[leaf]
        if isinstance(existing, list):
            if value and value not in existing:
                existing.append(value)
        elif isinstance(existing, dict):
            pass  # 이미 dict라면 아무것도 안 함
        elif existing != value and value not in [None, "", [], {}]:
            node[leaf] = [existing, value]






def get_tree():
    return tree

def refactor(tree: dict) -> dict:
    """
    트리 내 중복된 모든 노드를 자동 탐색하여 병합.
    :param tree: 트리 딕셔너리
    :return: 병합된 새 트리
    """
    name_locations = defaultdict(list)
    name_values = defaultdict(list)

    def collect(node, path, parent=None):
        if not isinstance(node, dict):
            return

        for key, value in list(node.items()):
            new_path = path + [key]
            if isinstance(value, dict):
                name_locations[key].append(path)  # path는 key의 부모 경로
                name_values[key].append(value)
                collect(value, new_path, node)

    collect(tree, [])

    # 중복 이름만 추림 (2개 이상 등장하는 키만)
    duplicates = {name for name, paths in name_locations.items() if len(paths) > 1}

    for name in duplicates:
        paths = name_locations[name]
        values = name_values[name]

        # 병합 위치 결정: 가장 자주 등장한 경로 (깊이 우선)
        target_path = max(
            [(p, paths.count(p)) for p in set(paths)],
            key=lambda x: (x[1], len(x[0]))
        )[0]

        # 병합 데이터 만들기
        merged = {}
        for v in values:
            merged.update(v)

        # 기존 노드 삭제
        def delete_all(node, path):
            if not isinstance(node, dict):
                return
            for key, value in list(node.items()):
                if key == name:
                    del node[key]
                else:
                    delete_all(value, path + [key])
        delete_all(tree, [])

        # 병합 위치 삽입
        current = tree
        for part in target_path:
            if part not in current or not isinstance(current[part], dict):
                current[part] = {}
            current = current[part]
        if name in current:
            current[name].update(merged)
        else:
            current[name] = merged

    return tree
