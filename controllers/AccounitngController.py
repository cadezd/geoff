import os
import re
from datetime import datetime

import pandas as pd

df_taxses: pd.core.frame.DataFrame = pd.read_excel(os.path.join('assets', 'ddv', 'BJI.xlsx'))
SETTINGS: dict = {
    'FONT_SIZE': 9,
    'DATE_FORMAT': '%m/%Y',
    'SORT_KONTE_DESC': False,
    'SORT_TAX_DESC': True,
    'KONTE_NOT_VALID': [270600],
    'KONTE_EXCEPTIONS': [500700],
    'HEIGHT': 55,
    'WIDTH': 55,
    'MARGIN': 2.5
}


def pridobi_osnove(osnove_data: pd.core.frame.DataFrame, taxses_data: pd.core.frame.DataFrame) -> dict[
                                                                                                  float: float]:
    grouped_tax_data: dict = dict()

    # drop rows that have NaN values in Splošna knjižna skupina izdelka column
    osnove_data = osnove_data.dropna(subset=['Splošna knjižna skupina izdelka'])

    # drop rows that dont have valid konte
    osnove_data = osnove_data[~osnove_data['Št. GK konta'].isin(SETTINGS['KONTE_NOT_VALID'])]

    # group by Št. GK konta and Knjižna skupina izdelka za DDV and sum the Znesek v breme2 and Znesek v dobro2
    grouped: pd.core.frame.DataFrame = osnove_data.groupby(['Št. GK konta', 'Knjižna skupina izdelka za DDV']).agg({
        'Znesek v breme2': 'sum',
        'Znesek v dobro2': 'sum',
    }).reset_index()

    # handling the exceptions (like KONTO 500700) where you ignore the other kontos
    # and keep only the ones that are in the exceptions to calculate the taxes
    if any(grouped['Št. GK konta'].isin(SETTINGS['KONTE_EXCEPTIONS'])):
        grouped = grouped[grouped['Št. GK konta'].isin(SETTINGS['KONTE_EXCEPTIONS'])]

    # keep only the columns that we need
    grouped = grouped[['Knjižna skupina izdelka za DDV', 'Znesek v breme2', 'Znesek v dobro2']]

    # group Osnove and DDV based on the DDV value
    for i, data in grouped.iterrows():
        DDV_vrednost: float = \
            taxses_data[taxses_data['Šifra'] == data['Knjižna skupina izdelka za DDV']]['formula'].values[0]
        v_breme: float = data['Znesek v breme2']
        v_dobro: float = data['Znesek v dobro2']

        if DDV_vrednost not in grouped_tax_data:
            grouped_tax_data[DDV_vrednost] = 0

        grouped_tax_data[DDV_vrednost] += v_breme - v_dobro if v_breme > 0 and v_dobro > 0 else v_breme

    return dict(sorted(grouped_tax_data.items(), reverse=SETTINGS['SORT_TAX_DESC']))


class ReceiptRecord:
    def __init__(self, receipt_data: pd.core.frame.DataFrame):
        # pridobi NRA
        self.nra: str = receipt_data['Št. dokumenta'].values[0]

        # pridobi DPR
        self.dpr: str = receipt_data[receipt_data['Vrsta dokumenta'] != 'Plačilo']['Opis'].values[0].split(' ')[-1]

        # pridobi Št. zunanjega dokumenta
        # poskrbi, da ne vzame št. zunanjega dokumenta, ki je plačilo (tam je napisan NRA)
        self.szd: str = receipt_data[receipt_data['Vrsta dokumenta'] != 'Plačilo']['Št. zunanjega dokumenta'].values[0]

        # pridobi Datum knjiženja
        self.datum_ddv: datetime = pd.to_datetime(receipt_data['Datum DDV'].values[0])

        # pridobi datum knjiženja
        self.datum_obdobje: datetime = pd.to_datetime(receipt_data['Datum knjiženja'].values[0])

        # pridobi OSNOVE
        osnove_data: pd.core.frame.DataFrame = receipt_data[
            ['Št. GK konta',
             'Splošna knjižna skupina izdelka',
             'Knjižna skupina izdelka za DDV',
             'Znesek v breme2',
             'Znesek v dobro2',
             'Znesek2']
        ]
        self.osnove_davki: dict[float: list[float]] = pridobi_osnove(osnove_data, df_taxses)

        # pridobi KONTE
        self.konte: list[str] = receipt_data['Št. GK konta'].unique().astype(str).tolist()
        self.konte = sorted(self.konte, reverse=SETTINGS['SORT_KONTE_DESC'])

        # pridobi knjižil
        self.knjizil: str = receipt_data['ID uporabnika'].values[0]
        self.knjizil = \
            '. '.join([n[0] for n in re.split(r'\.|\s', self.knjizil) if len(n) > 0]) + '.' \
                if self.knjizil and not pd.isna(self.knjizil) else '/'

    def set_nra(self, nra: str) -> str | None:
        if not nra or (nra and not nra.strip()):
            raise ValueError('Manjka NRA')

        self.nra = nra.strip()
        return self.nra

    def set_dpr(self, dpr: str) -> str | None:
        if not dpr or (dpr and not dpr.strip()):
            raise ValueError('Manjka DPR')

        self.dpr = dpr.strip()
        return self.dpr

    def set_szd(self, szd: str) -> str | None:
        if not szd or (szd and not szd.strip()):
            raise ValueError('Manjka Št. zunanjega dokumenta')

        self.szd = szd.strip()
        return self.szd

    def set_datum_ddv(self, datum_ddv: str) -> str | None:
        if not datum_ddv or (datum_ddv and not datum_ddv.strip()):
            raise ValueError('Manjka Datum DDV')

        if re.match(r'^\d{2}/\d{4}$', datum_ddv) is None:
            raise ValueError('Datum ni v formatu mm/yyyy')

        try:
            self.datum_ddv = datetime.strptime(datum_ddv, SETTINGS['DATE_FORMAT'])
            return datum_ddv
        except ValueError:
            raise ValueError('Datum ni veljaven')

    def set_datum_obdobje(self, datum_obdobje: str) -> str | None:
        if not datum_obdobje or (datum_obdobje and not datum_obdobje.strip()):
            raise ValueError('Manjka Datum obdobje')

        if re.match(r'^\d{2}/\d{4}$', datum_obdobje) is None:
            raise ValueError('Datum ni v formatu mm/yyyy')

        try:
            self.datum_obdobje = datetime.strptime(datum_obdobje, SETTINGS['DATE_FORMAT'])
            return datum_obdobje
        except ValueError:
            raise ValueError('Datum ni veljaven')

    def set_osnova(self, osnova: float, value: str) -> str | None:
        if osnova not in {22, 9.5, 0}:
            raise ValueError('Napačna osnova DDV')

        if not value or (value and not value.strip()):
            value = '0.0'

        # Replace all commas with '.'
        value = re.sub(r',', '.', value)

        try:
            value = round(float(value), 2)

            if value == 0:
                if osnova in self.osnove_davki:
                    del self.osnove_davki[osnova]
            else:
                if osnova not in self.osnove_davki:
                    self.osnove_davki[osnova] = 0
                self.osnove_davki[osnova] = value

            # Order the dictionary by the key
            self.osnove_davki = dict(sorted(self.osnove_davki.items(), reverse=SETTINGS['SORT_TAX_DESC']))

            return str(value)

        except ValueError:
            raise ValueError('Vrednost ni veljavna')

    def set_konte(self, konte: str) -> str | None:
        if not konte or (konte and not konte.strip()):
            raise ValueError('Manjka Konte')

        # Remove all spaces
        konte = re.sub(r'\s', '', konte)

        # There can't be 2 consecutive commas
        konte = re.sub(r',+', ',', konte)

        # Remove the last comma if it exists
        if konte and konte[-1] == ',':
            konte = konte[:-1]

        # Remove the first comma if it exists
        if konte and konte[0] == ',':
            konte = konte[1:]

        # Replace all commas with ', '
        konte = re.sub(r',', ', ', konte)

        if len(konte) == 0:
            raise ValueError('Manjkajo konte')

        self.konte = konte.split(', ')
        return konte

    def __str__(self):
        return f"""
#### **{self.nra if self.nra else 'NEZNAN NRA'}** ({self.szd if self.szd else 'NEZNANA ŠT. ZUNANJEGA DOKUMENTA'})

#### {self.dpr if self.dpr else 'NEZNAN DPR'}

#### **DDV:** {datetime.strftime(self.datum_ddv, '%m/%Y') if self.datum_ddv else 'NEZNAN DATUM DDV'}, **Obdobje:** {datetime.strftime(self.datum_obdobje, '%m/%Y') if self.datum_obdobje else 'NEZNAN DATUM KNJIŽENJA'}

|**%**| **Osnova** | **DDV**    |
|-----|------------|------------|
{''.join([f"|**{int(tax) if int(tax) == tax else tax}%**| {round(base, 2)}€ | {round(base * (tax / 100.0), 2)}€ |\n" for tax, base in self.osnove_davki.items()])}

#### **Konto:** {', '.join(self.konte if self.konte else ['/'])}

#### **Knjižil:** {self.knjizil if self.knjizil else '/'}
                        """

    def __lt__(self, other):
        return self.dpr < other.dpr


class AccountingController:
    def __init__(self):
        ...
