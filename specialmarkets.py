import constants
from mathutils import *


class SpecialMarkets:
    MSG_FA = 'لیست داده های وب سرویس'

    ID_FA = 'شناسه شاخص'
    TITLE_FA = 'عنوان شاخص'
    SLUG_FA = 'کلید شاخص'
    PRICE_FA = 'قیمت شاخص به ریال'
    DELTA_FA = 'میزان تغییر'
    DELTA_PERCENTAGE_FA = 'درصد تغییر'
    DELTA_TYPE_FA = 'نوع تغییر'
    OPENING_FA = 'نرخ بازگشایی شاخص'
    HIGH_FA = 'بالاترین نرخ امروز'
    LOW_FA = 'پایین ترین نرخ امروز'
    TIME_FA = 'زمان آخرین نرخ به فرمت غیر ماشینی'
    UPDATED_AT_FA = 'زمان آخرین نرخ به فرمت دیتابیسی'

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

    def __str__(self) -> str:
        return f"{self.ID_FA}: {self.sp_id}\n\n" \
               f"{self.TITLE_FA}: {self.title}\n\n" \
               f"{self.SLUG_FA}: {self.slug}\n\n" \
               f"{self.PRICE_FA}: {convert_int_currency(self.price)}\n\n" \
               f"{self.DELTA_FA}: {self.delta}\n\n" \
               f"{self.DELTA_PERCENTAGE_FA}: {self.delta_percentage}\n\n" \
               f"{self.DELTA_TYPE_FA}: {self.delta_type}\n\n" \
               f"{self.OPENING_FA}: {self.opening_index}\n\n" \
               f"{self.HIGH_FA}: {convert_int_currency(self.high)}\n\n" \
               f"{self.LOW_FA}: {convert_int_currency(self.low)}\n\n" \
               f"{self.TIME_FA}: {self.time}\n\n" \
               f"{self.UPDATED_AT_FA}: {convert_date_jalili(self.updated_at)}\n\n"

    def get_html(self) -> str:
        elbd = f"{constants.EMOJI_LARGE_BLUE_DIAMOND} "
        esbd = f"{constants.EMOJI_SMALL_BLUE_DIAMOND} "
        return f"{elbd}<b>{self.MSG_FA}</b>{(' ' * 60)}{constants.EMPTY_TRICK}\n\n" \
               f"{esbd}<b>{self.ID_FA}</b>: {self.sp_id}\n\n" \
               f"{esbd}<b>{self.TITLE_FA}</b>: {self.title}\n\n" \
               f"{esbd}<b>{self.SLUG_FA}</b>: {self.slug}\n\n" \
               f"{esbd}<b>{self.PRICE_FA}</b>: {convert_int_currency(self.price)}\n\n" \
               f"{esbd}<b>{self.DELTA_FA}</b>: {convert_int_currency(self.delta)}\n\n" \
               f"{esbd}<b>{self.DELTA_PERCENTAGE_FA}</b>: {self.delta_percentage}\n\n" \
               f"{esbd}<b>{self.DELTA_TYPE_FA}</b>: {self.delta_type}\n\n" \
               f"{esbd}<b>{self.OPENING_FA}</b>: {convert_int_currency(self.opening_index)}\n\n" \
               f"{esbd}<b>{self.HIGH_FA}</b>: {convert_int_currency(self.high)}\n\n" \
               f"{esbd}<b>{self.LOW_FA}</b>: {convert_int_currency(self.low)}\n\n" \
               f"{esbd}<b>{self.TIME_FA}</b>: {self.time}\n\n" \
               f"{esbd}<b>{self.UPDATED_AT_FA}</b>: {convert_date_jalili(self.updated_at)}\n\n"


class Mesghal(SpecialMarkets):
    MESGHAL_TEXT = 'mesghal'
    MESGHAL_MSG_FA = 'لیست قیمت لحظه‌ای مثقال'
    MESGHAL_TIME_FA = 'زمان‌بروزرسانی'
    MESGHAL_BUY_FA = 'قیمت‌خرید'
    MESGHAL_SELL_FA = 'قیمت‌فروش'
    MESGHAL_RAW_FA = 'قیمت‌اصلی'

    MESGHAL_SELL_RATE = 0  # Rial
    MESGHAL_BUY_RATE = 0  # Rial

    MESGHAL_ID = 137119

    SELL_PRICE_FA = 'قیمت‌ فروش'
    BUY_PRICE_FA = 'قیمت ‌خرید‌'

    def __init__(self, id, title, slug, p, d, dp, dt, o, h, l, t, updated_at, sell_rate, buy_rate) -> None:
        super().__init__(id, title, slug, p, d, dp, dt, o, h, l, t, updated_at)
        self.sell_price = self.price + sell_rate
        self.buy_price = self.price - buy_rate

    def __str__(self) -> str:
        return f"{super().__str__()}" \
               f"{self.SELL_PRICE_FA}</b>: {convert_int_currency(self.sell_price)}\n\n" \
               f"{self.BUY_PRICE_FA}</b>: {convert_int_currency(self.buy_price)}\n\n"

    def get_html(self) -> str:
        esbd = f"{constants.EMOJI_SMALL_BLUE_DIAMOND} "
        return f"{super().get_html()}" \
               f"{esbd}<b>{self.SELL_PRICE_FA}</b>: {convert_int_currency(self.sell_price)}\n\n" \
               f"{esbd}<b>{self.BUY_PRICE_FA}</b>: {convert_int_currency(self.buy_price)}\n\n" \
               f"{constants.EMPTY_TRICK}"

    def get_mesghal_html(self, is_raw):
        title = f"{constants.EMOJI_BANK} <b>{self.MESGHAL_MSG_FA}</b>{(' ' * 30)}" \
                f"{constants.EMPTY_TRICK}\n\n"

        raw = f"{constants.EMOJI_MONEY_BAG} #{self.MESGHAL_RAW_FA}: " \
              f"<b>{convert_digit_en_fa(convert_int_currency(self.price))}</b>\n\n"

        rates = f"{constants.EMOJI_BLACK_CLUB} #{self.MESGHAL_SELL_FA}: " \
                f"<b>{convert_digit_en_fa(convert_int_currency(self.sell_price))}</b>\n\n" \
                f"{constants.EMOJI_BLACK_SPADE} #{self.MESGHAL_BUY_FA}: " \
                f"<b>{convert_digit_en_fa(convert_int_currency(self.buy_price))}</b>\n\n\n\n"
        time = f"{constants.EMOJI_CLOCK_FACE_TWO} <b>{self.MESGHAL_TIME_FA}:</b> " \
               f"{get_jalili_format(convert_date_jalili(self.updated_at), True, True)}\n\n" \
               f"{constants.EMPTY_TRICK}"

        return title + (raw if is_raw else '') + rates + time
