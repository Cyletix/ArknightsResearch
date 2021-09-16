while(True):
    title_list=[]
    while(True):
        temp=input()
        if temp=='.':
            break
        title_list.append(temp)


    new_title_list=[]
    for title in title_list:
        if title.find('-')==-1:
            new_title_list.append(temp+title)
        else:
            temp=title
            new_title_list.append(temp)

    for title in new_title_list:
        print(title)
