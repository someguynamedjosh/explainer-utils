from bpy.types import Scene, Depsgraph, Object
from explainer_utils import bootstrap_utils
from explainer_utils.alpha.visibility import reset_object_visibility


def select_set_hierarchy(root: Object, value: bool):
    if value:
        reset_object_visibility(root)
    root.select_set(value)
    for child in root.children:
        select_set_hierarchy(child, value)


# Returns the first direct/indirect parent of the object where
# ${obj.group_with_children}
def first_grouped_parent(obj: Object):
    parent = obj.parent
    if parent is None:
        return None
    elif parent.group_with_children:
        return parent
    else:
        return first_grouped_parent(parent)


# I'm not going to bother commenting it because at the time of writing, I
# have no idea how it works, it just does.
# Maybe this vague diagram will help:
# X=Breached, unselected
# S=Breached, selected
# s=selected
# o=unselected
#
#         X <- Selecting this causes all children to be selected, because it is already breached.
#        / \
#       o   \ <- Selecting that causes that and all its children to be selected, because its parent is already breached.
#     /      S <- Selecting this causes all children to be selected, because it is already breached.
#    o      / \ <- Selecting that will cause its parent and all children to be selected, because that parent is not already breached.
#          s   s <- Selecting this will cause only that to be selected (and now breached), because its parent is already breached.
def update(scene: Scene, depsgraph: Depsgraph):
    if scene.ignore_group_with_children:
        return
    objects_to_group_select = set()
    objects_to_flag_breached = set()

    for obj in scene.objects:
        if not obj.select_get():
            continue
        if obj.group_with_children and obj.xu_breached:
            objects_to_flag_breached.add(obj)
            objects_to_group_select.add(obj)
            continue
        highest_unbreached_parent = obj
        while True:
            next_candidate = first_grouped_parent(highest_unbreached_parent)
            if next_candidate is None:
                break
            elif next_candidate.xu_breached:
                break
            else:
                highest_unbreached_parent = next_candidate
        objects_to_flag_breached.add(highest_unbreached_parent)
        if highest_unbreached_parent.group_with_children:
            objects_to_group_select.add(highest_unbreached_parent)

    for obj in scene.objects:
        obj.xu_breached = False

    for obj in objects_to_group_select:
        select_set_hierarchy(obj, True)

    for obj in objects_to_flag_breached:
        obj.xu_breached = True
        parent = first_grouped_parent(obj)
        while parent is not None:
            parent.xu_breached = True
            parent = first_grouped_parent(parent)
    
    for layer in scene.view_layers:
        obj = layer.objects.active
        if obj is None:
            continue
        breached_parent = obj
        while breached_parent is not None and not breached_parent.xu_breached:
            breached_parent = first_grouped_parent(breached_parent)
        if breached_parent is not None:
            layer.objects.active = breached_parent


bootstrap_utils.update_listeners.append(update)
