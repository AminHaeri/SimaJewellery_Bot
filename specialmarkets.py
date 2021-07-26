from mathutils import *
import datetime

MESGHAL_TEXT = 'mesghal'
MESGHAL_MSG_FA = 'لیست قیمت لحظه‌ای مثقال'
MESGHAL_TIME_FA = 'زمان‌بروزرسانی'
MESGHAL_BUY_FA = 'قیمت‌خرید'
MESGHAL_SELL_FA = 'قیمت‌فروش'
MESGHAL_RAW_FA = 'قیمت‌اصلی'

MESGHAL_INDEX = 33

MESGHAL_UPRATE = 0  # Rial
MESGHAL_DOWNRATE = 0  # Rial


class SpecialMarkets:
    id_fa = 'شناسه شاخص'
    title_fa = 'عنوان شاخص'
    slug_fa = 'کلید شاخص'
    price_fa = 'قیمت شاخص به ریال'
    delta_fa = 'میزان تغییر'
    delta_percentage_fa = 'درصد تغییر'
    delta_type_fa = 'نوع تغییر'
    opening_index_fa = 'نرخ بازگشایی شاخص'
    high_fa = 'بالاترین نرخ امروز'
    low_fa = 'پایین ترین نرخ امروز'
    time_fa = 'زمان آخرین نرخ به فرمت غیر ماشینی'
    updated_at_fa = 'زمان آخرین نرخ به فرمت دیتابیسی'

    mesghal_id = 137119

    def __init__(self,
                 id,
                 title,
                 slug,
                 p,
                 d,
                 dp,
                 dt,
                 o,
                 h,
                 l,
                 t,
                 updated_at) -> None:
        self.sp_id = int(id)
        self.title = str(title)
        self.slug = str(slug)
        self.price = int(p)
        self.delta = int(d)
        self.delta_percentage = float(dp)
        self.delta_type = str(dt)
        self.opening_index = int(o)
        self.high = int(h)
        self.low = int(l)
        self.time = str(t)
        self.updated_at = datetime.datetime.strptime(updated_at, '%Y-%m-%d %H:%M:%S')
        self.buy_price = self.price
        self.sell_price = self.price

    def __str__(self) -> str:
        return f"{self.id_fa}: {self.sp_id}\n\n" \
               f"{self.title_fa}: {self.title}\n\n" \
               f"{self.slug_fa}: {self.slug}\n\n" \
               f"{self.price_fa}: {convert_int_currency(self.price)}\n\n" \
               f"{self.delta_fa}: {self.delta}\n\n" \
               f"{self.delta_percentage_fa}: {self.delta_percentage}\n\n" \
               f"{self.delta_type_fa}: {self.delta_type}\n\n" \
               f"{self.opening_index_fa}: {self.opening_index}\n\n" \
               f"{self.high_fa}: {convert_int_currency(self.high)}\n\n" \
               f"{self.low_fa}: {convert_int_currency(self.low)}\n\n" \
               f"{self.time_fa}: {self.time}\n\n" \
               f"{self.updated_at_fa}: {convert_date_jalili(self.updated_at)}\n\n"
