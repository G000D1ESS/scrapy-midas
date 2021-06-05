from pydantic import ValidationError
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem, NotConfigured
from scrapy.utils.misc import load_object


class DuplicatesOfferPipeline:

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter['offer_id'] in self.ids_seen:
            raise DropItem(f"Duplicate item found: {item!r}")
        else:
            self.ids_seen.add(adapter['offer_id'])
            return item


class PydanticPipeline:

    def __init__(self, crawler, pydantic_model, enabled):
        self.crawler = crawler
        self.stats = crawler.stats
        self.pydantic_model = load_object(pydantic_model)
        self.is_enabled = enabled

    @classmethod
    def from_crawler(cls, crawler):
        pydantic_model = crawler.settings.get('PYDANTIC_MODEL')
        enabled = crawler.settings.getbool('PYDANTIC_ENABLED', True)
        if enabled and pydantic_model is None:
            raise NotConfigured
        return cls(
            crawler=crawler,
            pydantic_model=pydantic_model,
            enabled=enabled,
        )

    def process_item(self, item, spider):
        if not self.is_enabled:
            return item
        adapter = ItemAdapter(item)
        try:
            return self.pydantic_model(**adapter.asdict()).dict()
        except ValidationError as error:
            self.stats.inc_value('pydantic/validation/errors')
            raise DropItem(f"ValidationError: {error}")
