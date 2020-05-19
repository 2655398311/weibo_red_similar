import pandas as pd

df = pd.read_excel(r"C:\Users\hjfan\Desktop\result_fans11.xlsx")
data = df.loc[:, ['platform_cid', 'fans_num', 'labels', 'active_fans', 'add_fans']]

sareis = {}

def get_fenzu():
    # 将同一个等级的数据cid存放到等级中
    #     sareis = {"150000": [cid1, cid2, ...], "3000000": [cid122, cid666, ...], ...}
    for i in range(0, 3000000, 150000):
        if i == 0:
            continue

        sareis[str(i)] = []
        for id, da in enumerate(data.fans_num):
            if i-150000 < da < i:
                sareis[str(i)].append(data.platform_cid[id])


def get_bfb(curcid, nextcid):
    # 获取当前cid对应的数据行
    currow = df[(df.platform_cid == curcid)]
    # 获取需要对比的cid及对应的数据行
    nextrow = df[(df.platform_cid == nextcid)]

    # 粉丝数量百分比，权重0.4
    nextfansnum = nextrow.fans_num.values[0]
    curfansnum = currow.fans_num.values[0]
    if nextfansnum > curfansnum:
        fans_bfb = (curfansnum / nextfansnum) * 0.4
    else:
        fans_bfb = (nextfansnum / curfansnum) * 0.4

    # 标签百分比，权重0.3
    curlabelist = currow.labels.values[0].split(',')
    nextlabelist = nextrow.labels.values[0].split(',')
    num = 0
    for w in nextlabelist:
        if w in curlabelist:
            num += 1
    lables_bfb = num/len(curlabelist)*0.3

    # 活跃粉丝百分比，权重0.2
    nextactfansnum = nextrow.active_fans.values[0]
    curactfansnum = currow.active_fans.values[0]
    if nextactfansnum > curactfansnum:
        active_bfb = (curactfansnum / nextactfansnum) * 0.2
    else:
        active_bfb = (nextactfansnum / curactfansnum) * 0.2

    # 新增粉丝百分比，权重0.1
    nextaddfansnum = nextrow.add_fans.values[0]
    curaddfansnum = currow.add_fans.values[0]
    if nextaddfansnum > curaddfansnum:
        add_bfb = (curaddfansnum / nextaddfansnum) * 0.1
    else:
        add_bfb = (nextaddfansnum / curaddfansnum) * 0.1
    # 百分比求和
    bfb = fans_bfb + lables_bfb + active_bfb + add_bfb

    return bfb 


get_fenzu()
raw = {}

for k, v in sareis.items():
    # 切片，不同进程处理不同的数据，一次循环处理一个等级
    # if int(k) > 300000:
    #     break
    raw[str(k)] = {}

    while len(v) >= 1:
        # 对当前等级中的每一个cid，与同等级中的其它cid数据进行对比求百分比
        # v是同一等级中的cid的列表集合
        # 每次获取一个，v中减少一个
        curcid = v.pop()
        # eg: {"150000": {"cid1": []}}
        raw[str(k)][str(curcid)] = []

        # 对同等级中的剩余的cid进行遍历，依次与上面pop获取的当前cid进行对比求百分比
        for m in v:
            nextcid = m
            # 求当前cid和nextcid的百分比
            bfb = get_bfb(curcid, nextcid)
            # 获取前10个百分比的数据
            if len(raw[str(k)][str(curcid)]) >=10:
                val = []
                for idx, o in enumerate(raw[str(k)][str(curcid)]):
                    val.append(o[1])
                val.sort()
                if bfb > min(val):
                    raw[str(k)][str(curcid)].pop(val.index(min(val)))
                    raw[str(k)][str(curcid)].append([nextcid, bfb])
            else:
                raw[str(k)][str(curcid)].append([nextcid, bfb])

# writer = pd.ExcelWriter('f:\\output.xlsx')
# line['level'].append(o)
#"level":[]
line = { "platform_cid": [], "platform_cid_xs": [], "score": []}
for o, g in raw.items():
    for a, b in g.items():
        for pp in b:
            line['platform_cid'].append(a)
            line['platform_cid_xs'].append(pp[0])
            line['score'].append(pp[1])
# print(line)
df1 = pd.DataFrame(data=line)
print(df1)
df1.to_excel('red_person_score.xlsx')
# df1.to_excel(writer, sheet_name='cx')
# writer.save()