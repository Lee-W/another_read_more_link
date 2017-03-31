# -*- coding: utf-8 -*-

from pelican import signals, contents
from pelican.generators import ArticlesGenerator


def insert_read_more_link(instance):
    if type(instance) != contents.Article:
        return

    if not instance._content:
        instance.has_summary = False
        return

    ANOTHER_READ_MORE_LINK = instance.settings.get('ANOTHER_READ_MORE_LINK',
                                                   'Continue ->')
    ANOTHER_READ_MORE_LINK_FORMAT = instance.settings.get(
        'ANOTHER_READ_MORE_LINK_FORMAT',
        '<a class="another-read-more-link" href="/{url}" >{text}</a>'
    )

    content = instance._content

    marker_location = content.find("<!--more-->") or content.find("<!-- more -->")

    if marker_location == -1:
        if hasattr(instance, '_summary') or 'summary' in instance.metadata:
            summary = instance._summary
        else:
            instance._summary = instance._content
            instance.has_summary = True
            return
    else:
        summary = content[0:marker_location]

    if ANOTHER_READ_MORE_LINK:
        if instance.settings.get('RELATIVE_URLS'):
            read_more_link = ANOTHER_READ_MORE_LINK_FORMAT.format(url=instance.url, text=ANOTHER_READ_MORE_LINK)
        else:
            absolute_url = '{}/{}'.format(instance.settings.get('SITEURL'), instance.url)
            read_more_link = ANOTHER_READ_MORE_LINK_FORMAT.format(url=absolute_url, text=ANOTHER_READ_MORE_LINK)
        summary = summary  + read_more_link

    # default_status was added to Pelican Content objects after 3.7.1.
    # Its use here is strictly to decide on how to set the summary.
    # There's probably a better way to do this but I couldn't find it.
    if hasattr(instance, 'default_status'):
        instance.metadata['summary'] = summary
    else:
        instance._summary = summary
    instance.has_summary = True


def run_plugin(generators):
    for generator in generators:
        if isinstance(generator, ArticlesGenerator):
            for article in generator.articles:
                insert_read_more_link(article)


def register():
    try:
        signals.all_generators_finalized.connect(run_plugin)
    except AttributeError:
        # NOTE: This may result in #314 so shouldn't really be relied on
        # https://github.com/getpelican/pelican-plugins/issues/314
        signals.content_object_init.connect(insert_read_more_link)
