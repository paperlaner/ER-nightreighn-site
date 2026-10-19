from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.urls import reverse_lazy

from .models import Author, Book, Comment, Favorite
from .forms import AuthorForm, BookForm, CommentForm
from django.views.generic import CreateView, DeleteView, DetailView, ListView


SCALING_MAP = {
    "Wylder": {"strength": "A", "dexterity": "B", "intelligence": "C", "faith": "C", "arcane": "C"},
    "Guardian": {"strength": "B", "dexterity": "C", "intelligence": "D", "faith": "C", "arcane": "C"},
    "Duchess": {"strength": "D", "dexterity": "B", "intelligence": "A", "faith": "B", "arcane": "C"},
    "Recluse": {"strength": "D", "dexterity": "C", "intelligence": "S", "faith": "S", "arcane": "C"},
    "Ironeye": {"strength": "C", "dexterity": "A", "intelligence": "D", "faith": "D", "arcane": "B"},
    "Raider": {"strength": "S", "dexterity": "C", "intelligence": "D", "faith": "D", "arcane": "C"},
    "Executor": {"strength": "C", "dexterity": "S", "intelligence": "D", "faith": "D", "arcane": "S"},
    "Revenant": {"strength": "C", "dexterity": "C", "intelligence": "B", "faith": "S", "arcane": "B"},
    "Scholar": {"strength": "D", "dexterity": "C", "intelligence": "S", "faith": "A", "arcane": "B"},
    "Undertaker": {"strength": "B", "dexterity": "C", "intelligence": "B", "faith": "C", "arcane": "A"},
}

ATTRIBUTE_MAP = {
    "Wylder": {"vigor": 14, "mind": 10, "endurance": 14, "strength": 14, "dexterity": 14, "intelligence": 8, "faith": 8, "arcane": 8},
    "Guardian": {"vigor": 16, "mind": 9, "endurance": 16, "strength": 15, "dexterity": 10, "intelligence": 7, "faith": 8, "arcane": 8},
    "Duchess": {"vigor": 11, "mind": 12, "endurance": 11, "strength": 9, "dexterity": 15, "intelligence": 13, "faith": 11, "arcane": 10},
    "Recluse": {"vigor": 10, "mind": 14, "endurance": 10, "strength": 8, "dexterity": 9, "intelligence": 16, "faith": 16, "arcane": 11},
    "Ironeye": {"vigor": 11, "mind": 10, "endurance": 12, "strength": 11, "dexterity": 16, "intelligence": 8, "faith": 8, "arcane": 12},
    "Raider": {"vigor": 15, "mind": 10, "endurance": 15, "strength": 17, "dexterity": 10, "intelligence": 7, "faith": 8, "arcane": 9},
    "Executor": {"vigor": 12, "mind": 10, "endurance": 12, "strength": 11, "dexterity": 17, "intelligence": 8, "faith": 8, "arcane": 15},
    "Revenant": {"vigor": 10, "mind": 14, "endurance": 10, "strength": 9, "dexterity": 10, "intelligence": 14, "faith": 17, "arcane": 12},
    "Scholar": {"vigor": 10, "mind": 16, "endurance": 10, "strength": 8, "dexterity": 10, "intelligence": 17, "faith": 14, "arcane": 12},
    "Undertaker": {"vigor": 13, "mind": 12, "endurance": 13, "strength": 14, "dexterity": 11, "intelligence": 12, "faith": 10, "arcane": 15},
}

ABILITIES_MAP = {
    "Wylder": {
        "passive": "Aerial Assault",
        "passive_description": "Усиливает давление в прыжке и даёт более безопасный вход в атаку с возвышений.",
        "skill": "Claw Shot",
        "skill_description": "Быстрый захват цели крюком для сокращения дистанции и продолжения комбо вблизи.",
        "ultimate": "Onslaught Stake",
        "ultimate_description": "Мощный рывок-казнь по линии с высоким взрывным уроном по приоритетной цели.",
    },
    "Guardian": {
        "passive": "Steel Guard",
        "passive_description": "Повышает устойчивость к входящему давлению и помогает держать фронт под фокусом врагов.",
        "skill": "Whirlwind",
        "skill_description": "Круговая атака вокруг себя, сбивающая темп противников и очищающая пространство рядом.",
        "ultimate": "Wings of Salvation",
        "ultimate_description": "Командная защитная способность: даёт окно выживания и стабилизации в тяжёлом замесе.",
    },
    "Duchess": {
        "passive": "Magnificent Poise",
        "passive_description": "Повышает эффективность уклонений и поддерживает высокий темп игры на мобильности.",
        "skill": "Restage",
        "skill_description": "Позволяет переигрывать размен, быстро менять позицию и открывать цель под бурст.",
        "ultimate": "Finale",
        "ultimate_description": "Серия быстрых ударов с сильным финишем для добивания ключевого противника.",
    },
    "Recluse": {
        "passive": "Elemental Defense",
        "passive_description": "Укрепляет защиту от стихийного урона и даёт стабильность против магических угроз.",
        "skill": "Magic Cocktail",
        "skill_description": "Комбинирует эффекты заклинаний для контроля зоны и гибкой поддержки команды.",
        "ultimate": "Soulblood Song",
        "ultimate_description": "Массовая магическая способность с усилением командного темпа и контроля боя.",
    },
    "Ironeye": {
        "passive": "Eagle Eye",
        "passive_description": "Улучшает контроль дистанции и повышает ценность точных попаданий по уязвимым целям.",
        "skill": "Marking Shot",
        "skill_description": "Помечает цель и создаёт окно для усиленного урона от себя и союзников.",
        "ultimate": "Single Shot",
        "ultimate_description": "Сфокусированный выстрел по приоритетной цели с высоким моментальным уроном.",
    },
    "Raider": {
        "passive": "Fighter's Resolve",
        "passive_description": "Даёт устойчивость в ближнем бою и усиливает выгодные силовые размены.",
        "skill": "Retaliate",
        "skill_description": "Контрудар после принятия давления, который ломает темп противника на короткой дистанции.",
        "ultimate": "Totem Stela",
        "ultimate_description": "Ставит тотемный эффект, усиливающий боевое присутствие и контроль участка поля.",
    },
    "Executor": {
        "passive": "Tenacity",
        "passive_description": "Поддерживает агрессивный стиль, позволяя дольше держать инициативу в дуэлях.",
        "skill": "Cursed Sword",
        "skill_description": "Усиленная техника клинка для точечного прокола обороны и высокого крит-потенциала.",
        "ultimate": "Aspects of the Crucible: Beast",
        "ultimate_description": "Трансформирующая ульта с резким пиком урона и сильным давлением вблизи.",
    },
    "Revenant": {
        "passive": "Necromancy",
        "passive_description": "Усиливает взаимодействие с призывами и увеличивает ценность командной поддержки.",
        "skill": "Summon Spirit",
        "skill_description": "Призывает духа для отвлечения, контроля пространства и дополнительного урона.",
        "ultimate": "Immortal March",
        "ultimate_description": "Массовый эффект поддержки, повышающий выживаемость и общий темп команды.",
    },
    "Scholar": {
        "passive": "Arcane Thesis",
        "passive_description": "Усиливает эффективность магических связок и командных магических бафов.",
        "skill": "Sigil Burst",
        "skill_description": "Разворачивает сигил, который наносит магический урон и сдерживает продвижение врагов.",
        "ultimate": "Grand Formula",
        "ultimate_description": "Массовое магическое усиление с высоким уроном по площади и контролем темпа боя.",
    },
    "Undertaker": {
        "passive": "Grave Pact",
        "passive_description": "Повышает выживаемость в затяжных разменах и синергию с эффектами статусов.",
        "skill": "Grave Hook",
        "skill_description": "Подтягивает цель, ломая позиционку врага и открывая окно для фокуса команды.",
        "ultimate": "Requiem Toll",
        "ultimate_description": "Тяжелая ульта с давлением в ближней зоне и дополнительным уроном по ослабленным целям.",
    },}

NIGHTLORD_BOSSES = [
    {
        "name": "Gladius, Beast of Night",
        "role": "Босс-охотник",
        "threat": "Высокая",
        "description": "Быстрый агрессор с резкими выпадами и наказанием за ошибки позиционирования.",
        "weakness": "Яд",
        "hp_1p": "6,117",
        "hp_2p": "Нет данных (Fextralife)",
        "hp_3p": "18,351",
    },
    {
        "name": "Maris, Fathom of Night",
        "role": "Магический босс",
        "threat": "Высокая",
        "description": "Контролирует дистанцию, комбинирует магию и зонирует безопасные точки.",
        "weakness": "Молния",
        "hp_1p": "10,896",
        "hp_2p": "Нет данных (Fextralife)",
        "hp_3p": "32,688",
    },
    {
        "name": "Libra, Creature of Night",
        "role": "Контроль боя",
        "threat": "Средняя/высокая",
        "description": "Сбивает ритм группы за счет контроля пространства и затяжных разменов.",
        "weakness": "Святость, яд, гниль, безумие",
        "hp_1p": "13,048",
        "hp_2p": "26,096",
        "hp_3p": "39,144",
    },
    {
        "name": "Nightlord Heolstar",
        "role": "Финальный босс",
        "threat": "Очень высокая",
        "description": "Доминирует арену давлением вблизи и сериями широких комбо.",
        "weakness": "Святость (1-я фаза), молния (2-я фаза)",
        "hp_1p": "4,984 / 11,214",
        "hp_2p": "Нет данных (Fextralife)",
        "hp_3p": "14,952 / 33,642",
    },
    {
        "name": "Adel, Baron of Night",
        "role": "Nightlord",
        "threat": "Очень высокая",
        "description": "Продвинутый Nightlord с резкими сменами фаз и высоким давлением.",
        "weakness": "Яд",
        "hp_1p": "10,018",
        "hp_2p": "Нет данных (Fextralife)",
        "hp_3p": "30,054",
    },
    {
        "name": "Fulghor, Champion of Nightglow",
        "role": "Nightlord",
        "threat": "Очень высокая",
        "description": "Агрессивный элитный босс с опасными разменами на средней дистанции.",
        "weakness": "Молния",
        "hp_1p": "11,894",
        "hp_2p": "23,788",
        "hp_3p": "35,682",
    },
    {
        "name": "Caligo, Miasma of Night",
        "role": "Nightlord",
        "threat": "Очень высокая",
        "description": "Контрольный Nightlord с упором на зонирование и затяжной прессинг.",
        "weakness": "Огонь",
        "hp_1p": "16,458",
        "hp_2p": "32,916",
        "hp_3p": "49,374",
    },
    {
        "name": "Gnoster, Wisdom of Night",
        "role": "Nightlord",
        "threat": "Очень высокая",
        "description": "Сложный босс на позиционку и правильный тайминг ротаций команды.",
        "weakness": "Огонь",
        "hp_1p": "12,234",
        "hp_2p": "24,468",
        "hp_3p": "36,702",
    },
]

DLC_BOSSES = [
    {
        "name": "The Balancers",
        "role": "DLC-босс",
        "threat": "Высокая",
        "description": "DLC-босс с чередованием стойкостей и наказанием за жадные атаки.",
        "weakness": "Нет точных данных",
        "hp_1p": "Нет точных данных",
        "hp_2p": "Нет точных данных",
        "hp_3p": "Нет точных данных",
    },
    {
        "name": "Traitorous Straghess",
        "role": "DLC-босс",
        "threat": "Очень высокая",
        "description": "DLC-босс с резкими выпадениями и смертельным давлением вблизи.",
        "weakness": "Нет точных данных",
        "hp_1p": "Нет точных данных",
        "hp_2p": "Нет точных данных",
        "hp_3p": "Нет точных данных",
    },
]

OTHER_BOSSES = [
    {"name": "Abductor Virgin", "role": "Полевой босс", "threat": "Средняя", "description": "Обычная версия без ночной модификации."},
    {"name": "Albinaurics", "role": "Полевой босс", "threat": "Средняя", "description": "Обычная версия без ночной модификации."},
    {"name": "Ancient Heroes of Zamor", "role": "Полевой босс", "threat": "Средняя", "description": "Обычная версия без ночной модификации."},
    {"name": "Ancestor Spirit", "role": "Полевой босс", "threat": "Средняя", "description": "Обычная версия без ночной модификации."},
    {"name": "Augur", "role": "Рейд-босс", "threat": "Высокая", "description": "Обычная версия без ночной модификации."},
    {"name": "Banished Knights", "role": "Полевой босс", "threat": "Средняя", "description": "Обычная версия без ночной модификации."},
    {"name": "Battlemages", "role": "Полевой босс", "threat": "Средняя", "description": "Обычная версия без ночной модификации."},
    {"name": "Beastmen of Farum Azula", "role": "Полевой босс", "threat": "Средняя", "description": "Обычная версия без ночной модификации."},
    {"name": "Bell Bearing Hunter", "role": "Полевой босс", "threat": "Высокая", "description": "Базовая форма, без night-версии."},
    {"name": "Blinding Elder Lion", "role": "Особый босс", "threat": "Высокая", "description": "Обычная версия без ночной модификации."},
    {"name": "Black Blade Kindred", "role": "Полевой босс", "threat": "Высокая", "description": "Обычная версия без ночной модификации."},
    {"name": "Black Knife Assassin", "role": "Полевой босс", "threat": "Средняя", "description": "Обычная версия без ночной модификации."},
    {"name": "Colossal Fingercreeper", "role": "Полевой босс", "threat": "Средняя", "description": "Обычная версия без ночной модификации."},
    {"name": "Crucible Knight", "role": "Полевой босс", "threat": "Высокая", "description": "Базовая форма, без night-версии."},
    {"name": "Crystalians", "role": "Полевой босс", "threat": "Средняя", "description": "Обычная версия без ночной модификации."},
    {"name": "Demi-Human Queen", "role": "Полевой босс", "threat": "Средняя", "description": "Базовая форма, без night-версии."},
    {"name": "Depraved Perfumer", "role": "Полевой босс", "threat": "Средняя", "description": "Обычная версия без ночной модификации."},
    {"name": "Elder Lion", "role": "Полевой босс", "threat": "Высокая", "description": "Обычная версия без ночной модификации."},
    {"name": "Equilibrious Beast", "role": "Рейд-босс", "threat": "Высокая", "description": "Обычная версия без ночной модификации."},
    {"name": "Erdtree Avatar", "role": "Полевой босс", "threat": "Средняя", "description": "Обычная версия без ночной модификации."},
    {"name": "Erdtree Burial Watchdogs", "role": "Полевой босс", "threat": "Средняя", "description": "Обычная версия без ночной модификации."},
    {"name": "Executor (Remembrance Boss)", "role": "Особый босс", "threat": "Высокая", "description": "Личный босс памяти, без night-версии."},
    {"name": "Fallen Nightfarers", "role": "Полевой босс", "threat": "Средняя", "description": "Обычная версия без ночной модификации."},
    {"name": "Fallingstar Beast", "role": "Полевой босс", "threat": "Высокая", "description": "Обычная версия без ночной модификации."},
    {"name": "Fire Monk", "role": "Полевой босс", "threat": "Средняя", "description": "Обычная версия без ночной модификации."},
    {"name": "Fire Prelates", "role": "Полевой босс", "threat": "Средняя", "description": "Обычная версия без ночной модификации."},
    {"name": "Flame Chariots", "role": "Полевой босс", "threat": "Средняя", "description": "Обычная версия без ночной модификации."},
    {"name": "Flying Dragon of the Hills", "role": "Полевой босс", "threat": "Высокая", "description": "Обычная версия без ночной модификации."},
    {"name": "Frenzied Flame Troll", "role": "Полевой босс", "threat": "Средняя", "description": "Обычная версия без ночной модификации."},
    {"name": "Godskin Noble", "role": "Полевой босс", "threat": "Высокая", "description": "Обычная версия без ночной модификации."},
    {"name": "Golden Hippopotamus", "role": "Полевой босс", "threat": "Высокая", "description": "Базовая форма, без night-версии."},
    {"name": "Guardian Golem", "role": "Полевой босс", "threat": "Средняя", "description": "Обычная версия без ночной модификации."},
    {"name": "Guardians of the Dew", "role": "Особый босс", "threat": "Высокая", "description": "Обычная версия без ночной модификации."},
    {"name": "Leonine Misbegotten", "role": "Полевой босс", "threat": "Высокая", "description": "Обычная версия без ночной модификации."},
    {"name": "Lordsworn Captain", "role": "Полевой босс", "threat": "Средняя", "description": "Обычная версия без ночной модификации."},
    {"name": "Magma Wyrm", "role": "Полевой босс", "threat": "Высокая", "description": "Обычная версия без ночной модификации."},
    {"name": "Mausoleum Knight", "role": "Полевой босс", "threat": "Средняя", "description": "Обычная версия без ночной модификации."},
    {"name": "Miranda Blossom", "role": "Полевой босс", "threat": "Средняя", "description": "Обычная версия без ночной модификации."},
    {"name": "Mountaintop Ice Dragon", "role": "Полевой босс", "threat": "Высокая", "description": "Обычная версия без ночной модификации."},
    {"name": "Night Idol", "role": "Особый босс", "threat": "Высокая", "description": "Особая версия босса, но не Nightlord."},
    {"name": "Night's Cavalry", "role": "Полевой босс", "threat": "Высокая", "description": "Базовая форма, без night-версии экспедиции."},
    {"name": "Nox Warriors", "role": "Полевой босс", "threat": "Средняя", "description": "Обычная версия без ночной модификации."},
    {"name": "Onestrike Gladiator", "role": "Особый босс", "threat": "Высокая", "description": "Обычная версия без ночной модификации."},
    {"name": "Oracle Envoys", "role": "Полевой босс", "threat": "Средняя", "description": "Обычная версия без ночной модификации."},
    {"name": "Raider (Remembrance Boss)", "role": "Особый босс", "threat": "Высокая", "description": "Личный босс памяти, без night-версии."},
    {"name": "Red Wolf of the King Consort", "role": "Полевой босс", "threat": "Высокая", "description": "Обычная версия без ночной модификации."},
    {"name": "Redmane Knights", "role": "Полевой босс", "threat": "Средняя", "description": "Обычная версия без ночной модификации."},
    {"name": "Royal Army Knights", "role": "Полевой босс", "threat": "Средняя", "description": "Обычная версия без ночной модификации."},
    {"name": "Royal Carian Knight", "role": "Полевой босс", "threat": "Высокая", "description": "Обычная версия без ночной модификации."},
    {"name": "Royal Revenant", "role": "Полевой босс", "threat": "Высокая", "description": "Базовая форма, без night-версии."},
    {"name": "Runebear", "role": "Полевой босс", "threat": "Средняя", "description": "Обычная версия без ночной модификации."},
    {"name": "Sanguine Noble", "role": "Полевой босс", "threat": "Высокая", "description": "Обычная версия без ночной модификации."},
    {"name": "Sentient Pest", "role": "Рейд-босс", "threat": "Высокая", "description": "Обычная версия без night-модификации."},
    {"name": "Snow Troll and Flying Dragon", "role": "Полевой босс", "threat": "Высокая", "description": "Обычная версия без ночной модификации."},
    {"name": "Stonedigger Troll", "role": "Полевой босс", "threat": "Средняя", "description": "Обычная версия без ночной модификации."},
    {"name": "Stray Bloodhound Knight", "role": "Особый босс", "threat": "Высокая", "description": "Обычная версия без ночной модификации."},
    {"name": "Troll", "role": "Полевой босс", "threat": "Средняя", "description": "Обычная версия без ночной модификации."},
    {"name": "Tunnel Crystalian", "role": "Особый босс", "threat": "Средняя", "description": "Обычная версия без ночной модификации."},
    {"name": "Ulcerated Tree Spirit", "role": "Полевой босс", "threat": "Высокая", "description": "Базовая форма, без night-версии."},
    {"name": "Valiant Gargoyle", "role": "Полевой босс", "threat": "Высокая", "description": "Базовая форма, без night-версии."},
    {"name": "Wormface", "role": "Полевой босс", "threat": "Средняя", "description": "Базовая форма, без night-версии."},
    {"name": "Wylder (Remembrance Boss)", "role": "Особый босс", "threat": "Высокая", "description": "Личный босс памяти, без night-версии."},
]

BOSS_IMAGE_MAP = {
    "gladius": "Новая папка/gladius-everdark-4-nightreign-full.jpg",
    "maris": "Новая папка/maris-2-nightreign-full.jpg",
    "libra": "Новая папка/libra-3-nightreign-full.jpg",
    "heol": "Новая папка/heolstor-3-nightreign-full.jpg",
    "adel": "Новая папка/adel-2-nightreign-full.jpg",
    "fulghor": "Новая папка/fulghor-2-nightreign-full.jpg",
    "caligo": "Новая папка/caligo-nightreign-full.jpg",
    "gnoster": "Новая папка/gnoster-1-nightreign-full.jpg",
    "balancers": "Новая папка/balancers-night-lord-boss-elden-ring-nightreign-wiki-guide.jpg",
    "straghess": "Новая папка/traitorous-straghess-dreglord-night-lord-boss-elden-ring-nightreign-wiki-guide.jpg",
}


def scale_hp_value(value, factor):
    missing_markers = ("Нет данных", "Нет точных данных")
    if not value or any(marker in value for marker in missing_markers):
        return value
    if "/" in value:
        parts = [part.strip() for part in value.split("/")]
        return " / ".join(scale_hp_value(part, factor) for part in parts)

    digits = value.replace(",", "").strip()
    if digits.isdigit():
        return f"{int(digits) * factor:,}"
    return value


def enrich_boss_data(boss):
    enriched = dict(boss)
    if enriched.get("hp_2p") in {"Нет данных (Fextralife)", "Нет точных данных"}:
        inferred_hp = scale_hp_value(enriched.get("hp_1p", ""), 2)
        if inferred_hp and "Нет" not in inferred_hp:
            enriched["hp_2p"] = inferred_hp

    if enriched["name"] == "The Balancers":
        enriched.update(
            {
                "weakness": "Оценочно: молния и давление по стойке",
                "hp_1p": "9,840 (оценка)",
                "hp_2p": "19,680 (оценка)",
                "hp_3p": "29,520 (оценка)",
            }
        )
    elif enriched["name"] == "Traitorous Straghess":
        enriched.update(
            {
                "weakness": "Оценочно: святость и кровотечение",
                "hp_1p": "11,460 (оценка)",
                "hp_2p": "22,920 (оценка)",
                "hp_3p": "34,380 (оценка)",
            }
        )

    return enriched


def with_boss_image(boss):
    enriched = enrich_boss_data(boss)
    name = boss["name"].lower()
    enriched["image"] = None
    enriched["slug"] = slugify(boss["name"])
    for key, image_path in BOSS_IMAGE_MAP.items():
        if key in name:
            enriched["image"] = image_path
            break
    return enriched


NIGHTLORD_CHARACTERS = [with_boss_image(boss) for boss in (NIGHTLORD_BOSSES + DLC_BOSSES)]
NIGHT_BOSSES_DAY1 = [
    with_boss_image({"name": "Battlefield Commander", "role": "Ночной босс (1-я ночь)", "threat": "Высокая", "description": "Появляется в конце 1-й ночи.", "weakness": "Колющий", "hp_1p": "3,162", "hp_2p": "6,324", "hp_3p": "9,486"}),
    with_boss_image({"name": "Bell Bearing Hunter", "role": "Ночной босс (1-я ночь)", "threat": "Высокая", "description": "Появляется в конце 1-й ночи.", "weakness": "Святость", "hp_1p": "4,552", "hp_2p": "Нет данных (Fextralife)", "hp_3p": "13,656"}),
    with_boss_image({"name": "Centipede Demon", "role": "Ночной босс (1-я ночь)", "threat": "Высокая", "description": "Появляется в конце 1-й ночи.", "weakness": "Рубящий", "hp_1p": "4,312", "hp_2p": "Нет данных (Fextralife)", "hp_3p": "12,936"}),
    with_boss_image({"name": "Duke's Dear Freja", "role": "Ночной босс (1-я ночь)", "threat": "Высокая", "description": "Появляется в конце 1-й ночи.", "weakness": "Дробящий", "hp_1p": "2,459", "hp_2p": "4,918", "hp_3p": "7,377"}),
    with_boss_image({"name": "Demi-Human Queen & Swordmaster", "role": "Ночной босс (1-я ночь)", "threat": "Средняя", "description": "Появляется в конце 1-й ночи.", "weakness": "Стандарт / Рубящий / Дробящий / Колющий", "hp_1p": "3,053", "hp_2p": "Нет данных (Fextralife)", "hp_3p": "9,159"}),
    with_boss_image({"name": "Gaping Dragon", "role": "Ночной босс (1-я ночь)", "threat": "Высокая", "description": "Появляется в конце 1-й ночи.", "weakness": "Дробящий", "hp_1p": "4,064", "hp_2p": "Нет данных (Fextralife)", "hp_3p": "12,192"}),
    with_boss_image({"name": "Grafted Monarch", "role": "Ночной босс (1-я ночь)", "threat": "Высокая", "description": "Появляется в конце 1-й ночи.", "weakness": "Стандарт / Рубящий / Дробящий / Колющий", "hp_1p": "4,684", "hp_2p": "9,368", "hp_3p": "14,052"}),
    with_boss_image({"name": "Royal Revenant", "role": "Ночной босс (1-я ночь)", "threat": "Высокая", "description": "Появляется в конце 1-й ночи.", "weakness": "Огонь", "hp_1p": "2,837", "hp_2p": "Нет данных (Fextralife)", "hp_3p": "8,511"}),
    with_boss_image({"name": "Smelter Demon", "role": "Ночной босс (1-я ночь)", "threat": "Высокая", "description": "Появляется в конце 1-й ночи.", "weakness": "Дробящий", "hp_1p": "5,118", "hp_2p": "Нет данных (Fextralife)", "hp_3p": "15,354"}),
    with_boss_image({"name": "Tibia Mariner & Those Who Live in Death", "role": "Ночной босс (1-я ночь)", "threat": "Средняя/высокая", "description": "Появляется в конце 1-й ночи.", "weakness": "Дробящий, святость", "hp_1p": "3,193", "hp_2p": "6,386", "hp_3p": "9,579"}),
    with_boss_image({"name": "Ulcerated Tree Spirit", "role": "Ночной босс (1-я ночь)", "threat": "Высокая", "description": "Появляется в конце 1-й ночи.", "weakness": "Рубящий, огонь, святость", "hp_1p": "3,260", "hp_2p": "Нет данных (Fextralife)", "hp_3p": "9,780"}),
    with_boss_image({"name": "Valiant Gargoyle", "role": "Ночной босс (1-я ночь)", "threat": "Высокая", "description": "Появляется в конце 1-й ночи.", "weakness": "Дробящий", "hp_1p": "6,153", "hp_2p": "Нет данных (Fextralife)", "hp_3p": "18,459"}),
    with_boss_image({"name": "Wormface", "role": "Ночной босс (1-я ночь)", "threat": "Средняя/высокая", "description": "Появляется в конце 1-й ночи.", "weakness": "Рубящий", "hp_1p": "4,821", "hp_2p": "Нет данных (Fextralife)", "hp_3p": "14,463"}),
]
NIGHT_BOSSES_DAY2 = [
    with_boss_image({"name": "Ancient Dragon", "role": "Ночной босс (2-я ночь)", "threat": "Высокая", "description": "Появляется в конце 2-й ночи.", "weakness": "Колющий", "hp_1p": "6,893", "hp_2p": "13,786", "hp_3p": "20,679"}),
    with_boss_image({"name": "Crucible Knight & Golden Hippopotamus", "role": "Ночной босс (2-я ночь)", "threat": "Высокая", "description": "Появляется в конце 2-й ночи.", "weakness": "Стандарт / Рубящий / Дробящий / Колющий", "hp_1p": "6,965", "hp_2p": "Нет данных (Fextralife)", "hp_3p": "20,895"}),
    with_boss_image({"name": "Dancer of the Boreal Valley", "role": "Ночной босс (2-я ночь)", "threat": "Очень высокая", "description": "Появляется в конце 2-й ночи.", "weakness": "Молния", "hp_1p": "3,380", "hp_2p": "Нет данных (Fextralife)", "hp_3p": "10,140"}),
    with_boss_image({"name": "Draconic Tree Sentinel & Royal Cavalrymen", "role": "Ночной босс (2-я ночь)", "threat": "Высокая", "description": "Появляется в конце 2-й ночи.", "weakness": "Стандарт / Рубящий / Дробящий / Колющий", "hp_1p": "4,718", "hp_2p": "Нет данных (Fextralife)", "hp_3p": "14,154"}),
    with_boss_image({"name": "Fell Omen", "role": "Ночной босс (2-я ночь)", "threat": "Высокая", "description": "Появляется в конце 2-й ночи.", "weakness": "Молния, святость", "hp_1p": "7,403", "hp_2p": "Нет данных (Fextralife)", "hp_3p": "22,209"}),
    with_boss_image({"name": "Full-Grown Fallingstar Beast", "role": "Ночной босс (2-я ночь)", "threat": "Высокая", "description": "Появляется в конце 2-й ночи.", "weakness": "Нет данных (Fextralife)", "hp_1p": "6,964", "hp_2p": "Нет данных (Fextralife)", "hp_3p": "20,892"}),
    with_boss_image({"name": "Godskin Noble & Apostle", "role": "Ночной босс (2-я ночь)", "threat": "Высокая", "description": "Появляется в конце 2-й ночи.", "weakness": "Нет данных (Fextralife)", "hp_1p": "Нет данных (Fextralife)", "hp_2p": "Нет данных (Fextralife)", "hp_3p": "Нет данных (Fextralife)"}),
    with_boss_image({"name": "Great Wyrm", "role": "Ночной босс (2-я ночь)", "threat": "Высокая", "description": "Появляется в конце 2-й ночи.", "weakness": "Рубящий", "hp_1p": "7,211", "hp_2p": "Нет данных (Fextralife)", "hp_3p": "21,633"}),
    with_boss_image({"name": "Nameless King", "role": "Ночной босс (2-я ночь)", "threat": "Очень высокая", "description": "Появляется в конце 2-й ночи.", "weakness": "Молния (1-я фаза), святость (2-я фаза)", "hp_1p": "2,211 / 4,779", "hp_2p": "Нет данных (Fextralife)", "hp_3p": "6,633 / 14,337"}),
    with_boss_image({"name": "Nox Dragonkin Soldier", "role": "Ночной босс (2-я ночь)", "threat": "Высокая", "description": "Появляется в конце 2-й ночи.", "weakness": "Рубящий", "hp_1p": "7,446", "hp_2p": "Нет данных (Fextralife)", "hp_3p": "22,338"}),
    with_boss_image({"name": "Outland Commander", "role": "Ночной босс (2-я ночь)", "threat": "Высокая", "description": "Появляется в конце 2-й ночи.", "weakness": "Нет данных (Fextralife)", "hp_1p": "4,643", "hp_2p": "Нет данных (Fextralife)", "hp_3p": "13,929"}),
    with_boss_image({"name": "Death Rite Bird", "role": "Ночной босс (2-я ночь)", "threat": "Высокая", "description": "Появляется в конце 2-й ночи.", "weakness": "Святость", "hp_1p": "4,751", "hp_2p": "Нет данных (Fextralife)", "hp_3p": "14,253"}),
]
FIELD_BOSSES = [with_boss_image(boss) for boss in OTHER_BOSSES if boss.get("role") == "Полевой босс"]

def get_nightlord(slug):
    for boss in NIGHTLORD_CHARACTERS:
        if boss["slug"] == slug:
            return boss
    return None


def build_attributes(book):
    attributes = ATTRIBUTE_MAP.get(book.title)
    if attributes:
        return attributes
    return {
        "vigor": max(8, min(20, book.year // 20)),
        "mind": max(8, min(20, book.pages // 5)),
        "endurance": max(8, min(20, (42 + (book.pages // 2)) // 4)),
        "strength": 10,
        "dexterity": 10,
        "intelligence": 10,
        "faith": 10,
        "arcane": 10,
    }


def build_level_15_stats(book):
    attributes = build_attributes(book)
    base_stamina = max(48, min(72, 42 + (book.pages // 2)))
    return {
        "hp": book.year + attributes["vigor"] * 6 + 24,
        "fp": book.pages + attributes["mind"] * 4 + 10,
        "stamina": base_stamina + max(6, attributes["endurance"] // 2),
    }


def build_character_card(book):
    scaling = SCALING_MAP.get(
        book.title,
        {"strength": "C", "dexterity": "C", "intelligence": "C", "faith": "C", "arcane": "C"},
    )
    return {
        "book": book,
        "hp": book.year,
        "fp": book.pages,
        "stamina": max(48, min(72, 42 + (book.pages // 2))),
        "level_15": build_level_15_stats(book),
        "scaling": scaling,
        "attributes": build_attributes(book),
        "abilities": ABILITIES_MAP.get(
            book.title,
            {
                "passive": "Unknown",
                "passive_description": "Описание отсутствует.",
                "skill": "Unknown",
                "skill_description": "Описание отсутствует.",
                "ultimate": "Unknown",
                "ultimate_description": "Описание отсутствует.",
            },
        ),
        "categories": [category.name for category in book.categories.all()],
    }


def home(request):
    books = list(Book.objects.select_related("author").prefetch_related("categories"))
    featured_books = [build_character_card(book) for book in books if book.is_featured][:4]
    latest_books = [build_character_card(book) for book in books]
    return render(
        request,
        "books/home.html",
        {
            "featured_books": featured_books,
            "latest_books": latest_books,
            "nightlord_characters": NIGHTLORD_CHARACTERS,
            "night_bosses_day1": NIGHT_BOSSES_DAY1,
            "night_bosses_day2": NIGHT_BOSSES_DAY2,
            "night_bosses_total": len(NIGHT_BOSSES_DAY1) + len(NIGHT_BOSSES_DAY2),
            "field_bosses": FIELD_BOSSES,
        },
    )


def book_list(request):
    query = request.GET.get("q", "").strip()
    books = Book.objects.select_related("author").prefetch_related("categories")
    if query:
        books = books.filter(title__icontains=query)

    characters = [build_character_card(book) for book in books]

    return render(
        request,
        "books/book_list.html",
        {
            "books": characters,
            "query": query,
        },
    )


def book_search_by_slug(request, slug):
    books = Book.objects.select_related("author").prefetch_related("categories")
    filtered_books = [
        build_character_card(book)
        for book in books
        if slugify(book.title) == slug or any(category.slug == slug for category in book.categories.all())
    ]

    return render(
        request,
        "books/book_list.html",
        {
            "books": filtered_books,
            "query": slug,
        },
    )


def book_detail(request, pk):
    book = get_object_or_404(
        Book.objects.select_related("author").prefetch_related("categories"),
        pk=pk,
    )
    if request.method == "POST":
        form = CommentForm(request.POST, user=request.user)
        if form.is_valid():
            form.save_for_target(user=request.user, book=book)
            messages.success(request, "ÐÐ¾Ð¼Ð¼ÐµÐ½ÑÐ°ÑÐ¸Ð¹ Ð´Ð¾Ð±Ð°Ð²Ð»ÐµÐ½.")
            return redirect("books:book_detail", pk=pk)
    else:
        form = CommentForm(user=request.user)

    comments = book.comments.select_related("user")
    is_favorite = request.user.is_authenticated and Favorite.objects.filter(user=request.user, book=book).exists()
    return render(
        request,
        "books/book_detail.html",
        {
            "character": build_character_card(book),
            "comment_form": form,
            "comments": comments,
            "comment_target_name": book.title,
            "is_favorite": is_favorite,
        },
    )


def nightlord_detail(request, slug):
    boss = get_nightlord(slug)
    if not boss:
        messages.warning(request, "ÐÐ°Ð¹ÑÐ»Ð¾ÑÐ´ Ð½Ðµ Ð½Ð°Ð¹Ð´ÐµÐ½.")
        return redirect("books:home")

    if request.method == "POST":
        form = CommentForm(request.POST, user=request.user)
        if form.is_valid():
            form.save_for_target(user=request.user, nightlord_slug=slug)
            messages.success(request, "ÐÐ¾Ð¼Ð¼ÐµÐ½ÑÐ°ÑÐ¸Ð¹ Ð´Ð¾Ð±Ð°Ð²Ð»ÐµÐ½.")
            return redirect("books:nightlord_detail", slug=slug)
    else:
        form = CommentForm(user=request.user)

    comments = Comment.objects.filter(nightlord_slug=slug).select_related("user")
    return render(
        request,
        "books/nightlord_detail.html",
        {
            "boss": boss,
            "comment_form": form,
            "comments": comments,
            "comment_target_name": boss["name"],
        },
    )


def book_detail_shortcut(request, pk):
    if Book.objects.filter(pk=pk).exists():
        return redirect("books:book_detail", pk=pk)
    messages.warning(request, f"Персонаж с ID {pk} не найден.")
    return redirect("books:book_list")


@login_required
def book_favorite_toggle(request, pk):
    if request.method != "POST":
        return redirect("books:book_detail", pk=pk)

    book = get_object_or_404(Book, pk=pk)
    favorite, created = Favorite.objects.get_or_create(user=request.user, book=book)
    if created:
        messages.success(request, "???????? ???????? ? ?????????.")
    else:
        favorite.delete()
        messages.info(request, "???????? ?????? ?? ??????????.")
    return redirect("books:book_detail", pk=pk)


def book_create(request):
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()
            messages.success(request, "Персонаж добавлен в каталог Nightreign.")
            return redirect(book.get_absolute_url())
    else:
        form = BookForm()

    return render(
        request,
        "books/book_form.html",
        {"form": form, "form_title": "Добавление карточки героя", "submit_label": "Сохранить"},
    )


def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            book = form.save()
            messages.success(request, "Карточка персонажа обновлена.")
            return redirect(book.get_absolute_url())
    else:
        form = BookForm(instance=book)

    return render(
        request,
        "books/book_form.html",
        {"form": form, "form_title": "Редактирование карточки", "submit_label": "Обновить"},
    )


def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        book.delete()
        messages.success(request, "Карточка персонажа удалена.")
        return redirect("books:book_list")
    return render(request, "books/book_confirm_delete.html", {"book": book})


def api_book_list(request):
    books = Book.objects.select_related("author").prefetch_related("categories")
    payload = [
        {
            "id": book.pk,
            "title": book.title,
            "role": book.role,
            "author": book.author.name,
            "categories": [category.name for category in book.categories.all()],
            "description": book.description,
            "cover": book.cover.url if book.cover else None,
            "official_art": book.official_art.url if book.official_art else None,
            "hp": book.year,
            "fp": book.pages,
            "is_featured": book.is_featured,
        }
        for book in books
    ]
    return JsonResponse(payload, safe=False)


def api_book_detail(request, pk):
    book = get_object_or_404(
        Book.objects.select_related("author").prefetch_related("categories"),
        pk=pk,
    )
    payload = {
        "id": book.pk,
        "title": book.title,
        "role": book.role,
        "author": book.author.name,
        "categories": [category.name for category in book.categories.all()],
        "description": book.description,
        "cover": book.cover.url if book.cover else None,
        "official_art": book.official_art.url if book.official_art else None,
        "hp": book.year,
        "fp": book.pages,
        "is_featured": book.is_featured,
    }
    return JsonResponse(payload)




class BookListPageView(ListView):
    model = Book
    template_name = "books/book_list_cbv.html"
    context_object_name = "books"


class BookDetailPageView(DetailView):
    model = Book
    template_name = "books/book_detail_cbv.html"
    context_object_name = "book"


class AuthorCreatePageView(CreateView):
    model = Author
    form_class = AuthorForm
    template_name = "books/author_form.html"
    success_url = reverse_lazy("books:author_create")


class AuthorDeletePageView(DeleteView):
    model = Author
    template_name = "books/author_confirm_delete.html"
    success_url = reverse_lazy("books:book_list_cbv")
    context_object_name = "author"
