import pandas as pd
import plotnine as p9
import numpy as np
from matplotlib import pyplot as plt

plt.rcParams['pdf.fonttype'] = 42
# plt.rcParams['font.sans-serif'] = ['Arial']
SIG_PCTL_RANGE = (1, 99)


# def draw_boxplot(df,results_path,pos,base_list,title):
#     item_list = ['Mean', 'STD', 'Median', 'Dwell_time']
#     plot_list=[]
#     for item in item_list:
#
#         sig_min, sig_max = np.percentile(df[item], SIG_PCTL_RANGE)
#         sig_diff = sig_max - sig_min
#         ylim_tuple = (sig_min - sig_diff * 0.1, sig_max + sig_diff * 0.1)
#
#         plot = p9.ggplot(df, p9.aes(x='position', y=item, fill='type')) \
#                + p9.theme_bw() \
#                +p9.geom_boxplot( outlier_shape='',position=p9.position_dodge(0.9),size=0.25) \
#                + p9.scale_fill_manual(values={"Sample": "#ff6f91", "Control": "#7389af"}) \
#                + p9.scale_x_discrete(labels=list(base_list)) \
#                + p9.theme(
#                     figure_size=(6, 3),
#                     panel_grid_minor=p9.element_blank(),
#                     axis_text=p9.element_text(size=13),
#                     axis_title=p9.element_text(size=13),
#                     title=p9.element_text(size=13),
#                     legend_position='none')\
#                + p9.ylim(ylim_tuple)\
#                + p9.labs(title=title, x=str(pos + 1), y=item)
#
#         plot.save(filename=results_path + "/" + item + "_boxplot.pdf", dpi=300)
#
# def draw_violin(df,results_path,pos,base_list,title):
#
#     item_list = ['Mean', 'STD', 'Median', 'Dwell_time']
#     for item in item_list:
#
#         sig_min, sig_max = np.percentile(df[item], SIG_PCTL_RANGE)
#         sig_diff = sig_max - sig_min
#         ylim_tuple = (sig_min - sig_diff * 0.1, sig_max + sig_diff * 0.1)
#
#         plot = p9.ggplot(df, p9.aes(x='position', y=item, fill='type')) \
#                + p9.geom_violin(style='left-right',position=p9.position_dodge(0),color='none',width=1.5) \
#                + p9.theme_bw() \
#                + p9.scale_fill_manual(values={"Sample": "#ff6f91", "Control": "#7389af"}) \
#                + p9.scale_x_discrete(labels=list(base_list)) \
#                + p9.theme(
#             figure_size=(6, 3),
#             panel_grid_minor=p9.element_blank(),
#             axis_text=p9.element_text(size=13),
#             axis_title=p9.element_text(size=13),
#             title=p9.element_text(size=13),
#             legend_position='none'
#         )\
#         + p9.ylim(ylim_tuple)
#
#         plot = plot + p9.labs(title=title, x=str(pos + 1), y=item)
#         # plot.render_matplotlib()
#         plot.save(filename=results_path + "/" + item + "_violin.pdf", dpi=300)
# print(plot)

def current_plot(df, results_path, pos, base_list, title):
    print("Start to plot ...")
    item_list = ['Mean', 'STD', 'Median', 'Dwell time']
    len_plot = (len(base_list)-1)//2
    pos_list = list(range(-len_plot+pos,len_plot+1+pos))
    pos_list = [str(num) for num in pos_list]
    new_df = pd.DataFrame()
    for item in item_list:
        # collect data
        temp = df[[item, 'Position', 'Group']].copy()
        temp.columns = ['value', 'Position', 'Group']
        temp.loc[:, 'stats'] = item
        if filter:
            sig_min, sig_max = np.percentile(temp['value'], SIG_PCTL_RANGE)
            ylim_tuple = [sig_min , sig_max]
            temp = temp[(temp['value'] >= ylim_tuple[0]) & (temp['value'] <= ylim_tuple[1])]
        new_df = pd.concat([new_df, temp], axis=0)
    new_df['Position']=new_df['Position'].astype(str)
    plot = p9.ggplot(new_df, p9.aes(x='Position', y="value", fill='Group')) \
           + p9.theme_bw() \
           + p9.scale_fill_manual(values={"Sample": "#F57070", "Control": "#9F9F9F", "Single": "#a3abbd"}) \
           + p9.scale_x_discrete(breaks=pos_list, labels=base_list) \
           + p9.theme(
        figure_size=(8, 8),
        panel_grid_minor=p9.element_blank(),
        axis_text=p9.element_text(size=13),
        axis_title=p9.element_text(size=13),
        title=p9.element_text(size=13),
        legend_position='bottom',
        legend_title=p9.element_blank(),
        strip_text=p9.element_text(size=13),
        strip_background=p9.element_rect(alpha=0),

    ) \
           + p9.facet_grid('stats ~', scales='free_y')
    plot = plot + p9.labs(title=title, x=str(pos + 1), y='')

    if new_df['Group'].drop_duplicates().shape[0] == 1:
        print("control files do not exist, will turn to the single mode")
        plot2 = plot + p9.geom_violin(color='none', position=p9.position_dodge(0.9), width=1)
        plot2 = plot2 + p9.geom_boxplot(outlier_shape='', position=p9.position_dodge(0.9), size=0.2, width=0.1)
        plot2.save(filename=results_path + "/current_single.pdf", dpi=300)
    else:
        plot1 = plot + p9.geom_boxplot(outlier_shape='', position=p9.position_dodge(0.9), size=0.2, width=0.75,alpha = 0.8)
        plot1.save(filename=results_path + "/Current_boxplot.pdf", dpi=300)
        plot2 = plot + p9.geom_violin(style='left-right', position=p9.position_dodge(0), color='none', width=1.5,alpha = 0.8)
        plot2.save(filename=results_path + "/current_violin.pdf", dpi=300)
    print('Figures are saved in '+results_path)


def draw_signal(df, start, base,start_index,end_index):
    df = pd.DataFrame(df)
    df.columns = ['raw']
    start=start[start_index:end_index]
    df=df[start[0]:start[-1]]
    df = df.reset_index()
    plot = p9.ggplot(df, p9.aes(x='index', y="raw")) \
           + p9.theme_bw() \
           + p9.geom_line() \
           + p9.theme(
        figure_size=(6, 3),
        panel_grid_minor=p9.element_blank(),
        axis_text=p9.element_text(size=13),
        axis_title=p9.element_text(size=13),
        title=p9.element_text(size=13),
        strip_text=p9.element_text(size=13),
        legend_position='none',
        strip_background=p9.element_rect(alpha=0)
    )
    # plot.save(filename="/home/zhguo/Dropbox/@labfiles/projects/GUO/ONT_showcase_tool/plot/signal.pdf", dpi=300)
    for item in start:
        plot = plot + p9.geom_vline(xintercept=item, linetype='dashed', color='red')
    print(plot)
    # plot.save(filename="/home/zhguo/Dropbox/@labfiles/projects/GUO/ONT_showcase_tool/plot/norm_signal_aligned.pdf", dpi=300)

def alignment_plot(final_feature,pos_list,base_list,title,pos,results_path):
    order_list = ['Match', 'A', 'T', 'C', 'G']
    category = pd.api.types.CategoricalDtype(categories=order_list, ordered=True)
    final_feature['variable'] = final_feature['variable'].astype(category)

    order_list = ['Sample', 'Control','Single']
    category = pd.api.types.CategoricalDtype(categories=order_list, ordered=True)
    final_feature['Group'] = final_feature['Group'].astype(category)

    plot = p9.ggplot(final_feature, p9.aes(x='Position', y="value", fill='variable')) \
           + p9.theme_bw() \
           + p9.geom_bar(stat='identity') \
           + p9.scale_x_continuous(breaks=pos_list, labels=base_list) \
           + p9.scale_fill_manual(values={"Match": "#D7D7D7",
                                          'T': "#C88776",
                                          'A': '#95B989',
                                          'G': '#FFCE9B',
                                          'C': '#7CB3C5'}) \
           + p9.theme(
        figure_size=(8, 4),
        panel_grid_minor=p9.element_blank(),
        axis_text=p9.element_text(size=13),
        axis_title=p9.element_text(size=13),
        title=p9.element_text(size=13),
        legend_position='bottom',
        legend_title=p9.element_blank(),
        strip_text=p9.element_text(size=13),
        strip_background=p9.element_rect(alpha=0),

    ) \
           + p9.facet_grid('Group ~', scales='free_y')
    plot = plot + p9.labs(title=title, x=str(pos), y='Coverage')
    plot.save(filename=results_path + "/alignment.pdf", dpi=300)
    print('Figures are saved in ' + results_path)

def plot_PCA(df,results_path):
    print("Start to do PCA analysis ...")
    from scipy.stats import zscore
    df.loc[:, 'Mean'] = zscore(df['Mean'])
    df.loc[:, 'Median'] = zscore(df['Median'])
    df.loc[:, 'STD'] = zscore(df['STD'])
    df.loc[:, 'Dwell time'] = zscore(np.log10(df['Dwell time']))

    from sklearn.decomposition import PCA
    pca = PCA(n_components=2)
    new_df = pd.DataFrame(pca.fit_transform(df[['Mean', 'Median', 'STD', 'Dwell time']]))
    new_df.columns = ['PC1', 'PC2']
    new_df = pd.concat([new_df, df['Group'].reset_index()], axis=1)
    plot = p9.ggplot(new_df, p9.aes(x='PC1', y='PC2', color='Group')) \
           + p9.theme_bw() \
           + p9.ylim(-4, 4) \
           + p9.xlim(-4, 4) \
           + p9.stat_density_2d() \
           + p9.scale_color_manual(values={"Sample": "#F57070", "Control": "#9F9F9F", "Single": "#a3abbd"}) \
           + p9.geom_point() \
           + p9.theme(
        figure_size=(5, 5),
        panel_grid_minor=p9.element_blank(),
        axis_text=p9.element_text(size=13),
        axis_title=p9.element_text(size=13),
        title=p9.element_text(size=13),
        legend_position='bottom',
        legend_title=p9.element_blank(),
        strip_text=p9.element_text(size=13),
        strip_background=p9.element_rect(alpha=0),
    )
    plot.save(filename=results_path + "/zscore_density.pdf", dpi=300)
