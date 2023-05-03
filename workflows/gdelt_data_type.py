
dtypes_events = {
    'GLOBALEVENTID': 'uint64',
    'SQLDATE': 'string',
    'MonthYear': 'uint32',
    'Year': 'uint32',
    'FractionDate': 'float64',
    'Actor1Code': 'string',
    'Actor1Name': 'string',
    'Actor1CountryCode': 'string',
    'Actor1KnownGroupCode': 'string',
    'Actor1EthnicCode': 'string',
    'Actor1Religion1Code': 'string',
    'Actor1Religion2Code': 'string',
    'Actor1Type1Code': 'string',
    'Actor1Type2Code': 'string',
    'Actor1Type3Code': 'string',
    'Actor2Code': 'string',
    'Actor2Name': 'string',
    'Actor2CountryCode': 'string',
    'Actor2KnownGroupCode': 'string',
    'Actor2EthnicCode': 'string',
    'Actor2Religion1Code': 'string',
    'Actor2Religion2Code': 'string',
    'Actor2Type1Code': 'string',
    'Actor2Type2Code': 'string',
    'Actor2Type3Code': 'string',
    'IsRootEvent': 'uint32',
    'EventCode': 'string',
    'EventBaseCode': 'string',
    'EventRootCode': 'string',
    'QuadClass': 'uint32',
    'GoldsteinScale': 'float32',
    'NumMentions': 'uint32',
    'NumSources': 'uint32',
    'NumArticles': 'uint32',
    'AvgTone': 'float32',
    'Actor1Geo_Type': 'string',
    'Actor1Geo_FullName': 'string',
    'Actor1Geo_CountryCode': 'string',
    'Actor1Geo_ADM1Code': 'string',
    'Actor1Geo_ADM2Code': 'string',
    'Actor1Geo_Lat': 'float32',
    'Actor1Geo_Long': 'float32',
    'Actor1Geo_FeatureID': 'string',
    'Actor2Geo_Type': 'string',
    'Actor2Geo_FullName': 'string',
    'Actor2Geo_CountryCode': 'string',
    'Actor2Geo_ADM1Code': 'string',
    'Actor2Geo_ADM2Code': 'string',
    'Actor2Geo_Lat': 'float32',
    'Actor2Geo_Long': 'float32',
    'Actor2Geo_FeatureID': 'string',
    'ActionGeo_Type': 'string',
    'ActionGeo_FullName': 'string',
    'ActionGeo_CountryCode': 'string',
    'ActionGeo_ADM1Code': 'string',
    'ActionGeo_ADM2Code': 'string',
    'ActionGeo_Lat': 'float32',
    'ActionGeo_Long': 'float32',
    'ActionGeo_FeatureID': 'string',
    'DATEADDED': 'string',
    'SOURCEURL': 'string'
}


dtypes_mentions = {
    'GLOBALEVENTID': 'uint64',
    'EventTimeDate': 'string',
    'MentionTimeDate': 'string',
    'MentionType': 'int64',
    'MentionSourceName': 'string',
    'MentionIdentifier': 'string',
    'SentenceID': 'int64',
    'Actor1CharOffset': 'int64',
    'Actor2CharOffset': 'int64',
    'ActionCharOffset': 'int64',
    'InRawText': 'int64',
    'Confidence': 'int64',
    'MentionDocLen': 'int64',
    'MentionDocTone': 'float64',
    'MentionDocTranslationInfo': 'string',
    'Extras': 'string'
}


dtypes_gkg = {
    'GKGRECORDID': 'string',
    'DATE': 'datetime64[ns]',
    'SourceCollectionIdentifier': 'string',
    'SourceCommonName': 'string',
    'DocumentIdentifier': 'string',
    'Counts': 'string',
    'V2Counts': 'string',
    'Themes': 'string',
    'V2Themes': 'string',
    'Locations': 'string',
    'V2Locations': 'string',
    'Persons': 'string',
    'V2Persons': 'string',
    'Organizations': 'string',
    'V2Organizations': 'string',
    'V2Tone': 'string',
    'Dates': 'string',
    'GCAM': 'string',
    'SharingImage': 'string',
    'RelatedImages': 'string',
    'SocialImageEmbeds': 'string',
    'SocialVideoEmbeds': 'string',
    'Quotations': 'string',
    'AllNames': 'string',
    'Amounts': 'string',
    'TranslationInfo': 'string',
    'Extras': 'string'
}
