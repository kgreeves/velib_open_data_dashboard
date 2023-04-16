import pandas as pd
from numpy import round
import matplotlib.pyplot as plt
import seaborn as sns
from app.modules.visualising import col_name_to_text


colors = ['#000080', '#B22222', '#008000', '#800080']

def plot_occupancy(data_pd: pd.DataFrame, x_col: str, y_col: str):

    max_capacity = max(data_pd[x_col].max(), data_pd[y_col].max())
    data_pd['fields.percent_occ'] = 100.*data_pd['fields.numbikesavailable']/data_pd['fields.capacity']
    perfect_dist = data_pd['fields.percent_occ'].mean()
    data_pd['fields.less_even_occ'] = data_pd['fields.percent_occ'] < perfect_dist

    with sns.axes_style("darkgrid"):
        g = sns.jointplot(data=data_pd, x=x_col, y=y_col, alpha=0.6,
        #g=sns.jointplot(data=data_pd, x=x_col, y=y_col, hue='fields.less_even_occ', alpha=0.6,
                                          marginal_kws=dict(binwidth=1), palette=['blue','magenta'])
        #sns.scatterplot(data=data_pd, x=x_col, y=y_col, hue='fields.less_even_occ', palette=['blue','magenta'], alpha= 0.6, ax=ax)

        sns.scatterplot(data=data_pd, x=x_col, y=y_col, alpha=0.6,ax=g.ax_joint)
        for i, percent in enumerate([0.5,0.75, 1.0, 0.01*perfect_dist]):
            g.ax_joint.plot([0, 0.92*max_capacity], [0, 0.92*percent*max_capacity], linestyle='--',
                    color=colors[i], alpha=0.5)
            g.ax_joint.annotate(f'{round(percent*100.,1)}%', xy=(0.94*max_capacity, 0.94*percent*max_capacity),
                        color=colors[i], size=12)
        '''
        ax.plot([0, max_capacity], [0, 0.75*max_capacity], 'g--', alpha=0.5, label='75% Occupied')
        ax.plot([0, max_capacity], [0, 1.0*max_capacity], 'b--', alpha=0.5, label='100% Occupied')
        ax.plot([0, max_capacity], [0, perfect_dist*max_capacity], 'm--', alpha=0.8,
                 label=f'{round(100.*perfect_dist,2)}% (Perfect Distribution) ')
        '''
    plt.xlabel(col_name_to_text(x_col))
    plt.ylabel(col_name_to_text(y_col))

    plt.xlim([0.,95.])
    plt.ylim([0.,100.])


    #plt.legend(bbox_to_anchor=(1.04, 1), borderaxespad=0)
    plt.show()


def plot_bikes_avail(data_pd: pd.DataFrame,capacity: int = None, y_col:str = None):

    x_col='fields.capacity';

    if y_col is None: y_col = 'fields.numbikesavailable'

    max_capacity = max(data_pd[x_col].max(), data_pd[y_col].max())
    data_pd['fields.percent_occ'] = data_pd[y_col]/data_pd['fields.capacity']
    perfect_dist = data_pd['fields.percent_occ'].mean()

    fig = plt.figure()


    if capacity is not None:
        ax = fig.add_subplot(111, aspect=0.5)
        plot_data = (data_pd
            [data_pd['fields.capacity'] == capacity]
            [y_col]
            .divide(capacity)
        )
        with sns.axes_style("darkgrid"):
            sns.kdeplot(data=plot_data, cut=0., ax=ax)

        ax.axvline(x=perfect_dist, ymin=0, ymax=1, color='m', linestyle='--', alpha=0.6)

    else:


        axs = fig.subplot_mosaic([['Left', 'TopRight'], ['Left', 'BottomRight']],
                                 gridspec_kw={'width_ratios': [2, 1]})

        with sns.axes_style("whitegrid"):
            sns.jointplot(data=data_pd, x=x_col, y=y_col, alpha=0.5,
                          ax=axs['Left'], marginal_kws=dict(bins=100))
            #sns.kdeplot(data=data_pd, x='fields.capacity', y=y_col,
             #           levels=15, fill=True, ax=axs['Left'])

            axs['Left'].plot([0, 0.96*max_capacity], [0, 0.96*perfect_dist*max_capacity], linestyle='--',
                    color='m', alpha=0.5)

            axs['Left'].set_xlabel(col_name_to_text(x_col))
            axs['Left'].set_ylabel(col_name_to_text(y_col))

            sns.histplot(data=data_pd, y=y_col, kde=True, ax=axs['TopRight'])
            sns.histplot(data=data_pd, x='fields.capacity', kde=True,  ax=axs['BottomRight'])



            '''
            for capacity in data_pd['fields.capacity'].unique():

                plot_data = (data_pd
                             [data_pd['fields.capacity'] == capacity]
                             ['fields.numbikesavailable']
                             .divide(capacity)
                             )

                if plot_data.shape[0] > 5:
                    sns.kdeplot(data=plot_data, clip=(0.0, 1.0), ax=ax)
            '''
    plt.show()