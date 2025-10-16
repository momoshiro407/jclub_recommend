CREATE OR REPLACE FUNCTION normalize_alnum(text)
RETURNS text AS $$
BEGIN
    RETURN translate(
        $1,
        'ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ０１２３４５６７８９',
        'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    );
END;
$$ LANGUAGE plpgsql IMMUTABLE;