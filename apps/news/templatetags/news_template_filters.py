from django import template

register = template.Library()


@register.filter
def page_bar(page):
    page_list = []
    # 把第一页一直显示
    if page.number != 1:
        page_list.append(1)
    # 如果这个数的前三个不是1就显示...
    if page.number - 3 > 1:
        page_list.append('...')
    # 显示这个数的前两个
    if page.number - 2 > 1:
        page_list.append(page.number - 2)
    # 显示这个数的前一个
    if page.number - 1 > 1:
        page_list.append(page.number - 1)
    # 显示这个数
    page_list.append(page.number)
    # 显示后第一页
    if page.paginator.num_pages > page.number + 1:
        page_list.append(page.number + 1)
    # 显示后第二页
    if page.paginator.num_pages > page.number + 2:
        page_list.append(page.number + 2)
    # 如果第三页不是最后一页就显示...
    if page.paginator.num_pages > page.number + 3:
        page_list.append('...')
    # 如果不是最后一页就一直显示最后一页
    if page.paginator.num_pages != page.number:
        page_list.append(page.paginator.num_pages)
    return page_list
