from easydict import EasyDict

# env_name = 'MiniGrid-Empty-8x8-v0'
# max_env_step = int(1e6)

# env_name = 'MiniGrid-FourRooms-v0'
# max_env_step = int(2e6)

env_name = 'MiniGrid-DoorKey-8x8-v0'
max_env_step = int(5e6)

# typical MiniGrid env id: {'MiniGrid-Empty-8x8-v0', 'MiniGrid-FourRooms-v0', 'MiniGrid-DoorKey-8x8-v0','MiniGrid-DoorKey-16x16-v0'},
# please refer to https://github.com/Farama-Foundation/MiniGrid for details.

# ==============================================================
# begin of the most frequently changed config specified by the user
# ==============================================================
seed = 0

collector_env_num = 8
n_episode = 8
evaluator_env_num = 3
continuous_action_space = False
K = 5  # num_of_sampled_actions
num_simulations = 50
update_per_collect = 200
batch_size = 256

# collector_env_num = 1
# n_episode = 1
# evaluator_env_num = 1
# num_simulations = 5
# update_per_collect = 2
# batch_size = 2

reanalyze_ratio = 0
random_collect_episode_num = 0
init_temperature_value_for_decay = 1.0
td_steps = 5
eval_sample_action = False

policy_entropy_loss_weight = 0.
# policy_entropy_loss_weight = 0.005
# threshold_training_steps_for_final_temperature = int(5e4)
threshold_training_steps_for_final_temperature = int(5e5)
eps_greedy_exploration_in_collect = False
# eps_greedy_exploration_in_collect = True
# ==============================================================
# end of the most frequently changed config specified by the user
# ==============================================================

minigrid_sampled_efficientzero_config = dict(
    exp_name=
    f'data_sez_ctree/{env_name}_sampled_efficientzero_ns{num_simulations}_upc{update_per_collect}_rr{reanalyze_ratio}_'
    f'eval-sample-{eval_sample_action}_pelw{policy_entropy_loss_weight}_temp-final-steps-{threshold_training_steps_for_final_temperature}_collect-eps-{eps_greedy_exploration_in_collect}-decay-linear-2e5-env_seed{seed}',
    env=dict(
        env_name=env_name,
        continuous=False,
        manually_discretization=False,
        collector_env_num=collector_env_num,
        evaluator_env_num=evaluator_env_num,
        n_evaluator_episode=evaluator_env_num,
        manager=dict(shared_memory=False, ),
    ),
    policy=dict(
        model=dict(
            observation_shape=2835,
            action_space_size=7,
            continuous_action_space=continuous_action_space,
            num_of_sampled_actions=K,
            model_type='mlp', 
            lstm_hidden_size=256,
            latent_state_dim=256,
            discrete_action_encoding_type='one_hot',
            norm_type='BN', 
        ),
        eval_sample_action=eval_sample_action,
        policy_entropy_loss_weight=policy_entropy_loss_weight,
        eps=dict(
            eps_greedy_exploration_in_collect=eps_greedy_exploration_in_collect,
            type='linear',
            start=1.,
            end=0.05,
            decay=int(2e5),
        ),
        random_collect_episode_num=random_collect_episode_num,
        td_steps=td_steps,
        manual_temperature_decay=True,
        # To make init policy be more random in sparse reward env.
        init_temperature_value_for_decay=init_temperature_value_for_decay,
        threshold_training_steps_for_final_temperature=threshold_training_steps_for_final_temperature,
        # TODO: test the effect
        # use_max_priority_for_new_data=False,
        # priority_prob_alpha=1,
        use_max_priority_for_new_data=True,
        priority_prob_alpha=0.6,
        cuda=True,
        env_type='not_board_games',
        game_segment_length=50,
        update_per_collect=update_per_collect,
        batch_size=batch_size,
        optim_type='AdamW',
        lr_piecewise_constant_decay=False,
        learning_rate=0.003,
        num_simulations=num_simulations,
        reanalyze_ratio=reanalyze_ratio,
        n_episode=n_episode,
        eval_freq=int(2e2),
        replay_buffer_size=int(1e6),  # the size/capacity of replay_buffer, in the terms of transitions.
        collector_env_num=collector_env_num,
        evaluator_env_num=evaluator_env_num,
    ),
)

minigrid_sampled_efficientzero_config = EasyDict(minigrid_sampled_efficientzero_config)
main_config = minigrid_sampled_efficientzero_config

minigrid_sampled_efficientzero_create_config = dict(
    env=dict(
        type='minigrid_lightzero',
        import_names=['zoo.minigrid.envs.minigrid_lightzero_env'],
    ),
    env_manager=dict(type='subprocess'),
    policy=dict(
        type='sampled_efficientzero',
        import_names=['lzero.policy.sampled_efficientzero'],
    ),
    collector=dict(
        type='episode_muzero',
        import_names=['lzero.worker.muzero_collector'],
    )
)
minigrid_sampled_efficientzero_create_config = EasyDict(minigrid_sampled_efficientzero_create_config)
create_config = minigrid_sampled_efficientzero_create_config

if __name__ == "__main__":
    # Users can use different train entry by specifying the entry_type.
    entry_type = "train_muzero"  # options={"train_muzero", "train_muzero_with_gym_env"}

    if entry_type == "train_muzero":
        from lzero.entry import train_muzero
    elif entry_type == "train_muzero_with_gym_env":
        """
        The ``train_muzero_with_gym_env`` entry means that the environment used in the training process is generated by wrapping the original gym environment with LightZeroEnvWrapper.
        Users can refer to lzero/envs/wrappers for more details.
        """
        from lzero.entry import train_muzero_with_gym_env as train_muzero

    train_muzero([main_config, create_config], seed=seed, max_env_step=max_env_step)