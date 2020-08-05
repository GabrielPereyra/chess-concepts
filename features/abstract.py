import click
import pandas as pd


def _is_feature(attr):
    return (
        not attr.startswith('__') and
        not attr.startswith('_') and
        attr not in ['features', 'feature_names', 'from_row', 'from_df']
    )


class Features:

    @classmethod
    def feature_names(cls):
        return [attr for attr in dir(cls) if _is_feature(attr)]

    def features(self):
        feature_dict = {}
        for feature_name in self.feature_names():
                feature_dict[feature_name] = getattr(self, feature_name)
        return feature_dict

    @classmethod
    def from_row(cls, row):
        return cls(row.fen)

    @classmethod
    def from_df(cls, df):
        feature_rows = []
        with click.progressbar(tuple(df.itertuples())) as rows:
            for row in rows:
                feature_instance = cls.from_row(row)
                feature_rows.append(feature_instance.features())
        return pd.DataFrame(feature_rows)