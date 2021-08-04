from explainer_utils import bootstrap_utils

bootstrap_utils.register_listeners.append(
    lambda: print('hey world!')
)

bootstrap_utils.unregister_listeners.append(
    lambda: print('bodobiwejye world!')
)
