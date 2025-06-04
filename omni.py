import json
def add_branch(tree, parent_key, child_key):
    def recurse(node):
        if isinstance(node, list):
            for item in node:
                recurse(item)
        elif isinstance(node, dict):
            for key, value in node.items():
                if key == parent_key:
                    if isinstance(value, list):
                        value.append({child_key: []})
                        print(f"✔️ Added branch '{child_key}' under '{parent_key}'")
                else:
                    recurse(value)

    recurse(tree)


def insert_parent(tree, old_key, new_key):
    def recurse(node):
        if isinstance(node, list):
            for i, item in enumerate(node):
                if isinstance(item, dict) and old_key in item:
                    # Gói item[old_key] vào new parent
                    old_value = item.pop(old_key)
                    node[i] = {new_key: [{old_key: old_value}]}
                    print(f"✔️ Inserted '{new_key}' above '{old_key}'")
                else:
                    recurse(item)
        elif isinstance(node, dict):
            for key in list(node.keys()):
                recurse(node[key])

    recurse(tree)


def remove_key_once(tree, target_key):
    removed = False

    def recurse(node, parent=None, idx_or_key=None):
        nonlocal removed
        if removed:
            return True  # dừng

        if isinstance(node, dict):
            if target_key in node:
                print(f"❌ Removed key '{target_key}' and its subtree.")
                del node[target_key]
                removed = True
                return True
            for key, val in node.items():
                if recurse(val, node, key):
                    return True

        elif isinstance(node, list):
            for i in range(len(node)):
                item = node[i]
                if isinstance(item, dict) and target_key in item:
                    print(f"❌ Removed key '{target_key}' and its subtree.")
                    del node[i]
                    removed = True
                    return True
                if recurse(item, node, i):
                    return True
        return False

    recurse(tree)


def find_path(data, target, path=None):
    if path is None:
        path = []

    if isinstance(data, dict):
        for key, value in data.items():
            if key == target:
                return path + [key]
            path.append(key)
            result = find_path(value, target, path)
            if result:
                return result
            path.pop()

    elif isinstance(data, list):
        for item in data:
            result = find_path(item, target, path)
            if result:
                return result

    else:
        if data == target:
            return path + [target]

    return None

def clean_data(data):
    if isinstance(data, dict):
        keys_to_delete = [k for k in data if not k.startswith("#")]
        for k in keys_to_delete:
            del data[k]
        for v in data.values():
            clean_data(v)
    elif isinstance(data, list):
        # Duyệt ngược để xóa phần tử không đúng điều kiện
        for i in range(len(data) - 1, -1, -1):
            item = data[i]
            if not (isinstance(item, str) and item.startswith("#")):
                del data[i]
            else:
                clean_data(item)