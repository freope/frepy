import pyper

from frestu.feature_extraction import ExtractorFeatureAbstract


class ExtractorLocalLevelSequentialSmooth(ExtractorFeatureAbstract):

    def __init__(
            self,
            col_feature, lag, m0, C0, dW, dV, 
            can_filter=False, can_smooth=False):
        self.__col_feature = col_feature
        self.__lag = lag
        self.__m0 = m0
        self.__C0 = C0
        self.__dW = dW
        self.__dV = dV
        self.__can_filter = 'TRUE' if can_filter else 'FALSE'
        self.__can_smooth = 'TRUE' if can_smooth else 'FALSE'
        self.__r = pyper.R(use_pandas='True')
        self.__r('library(dlm)')
    
    def extract(self, df):
        # インデックスを削除しないと R 側にアサインできない
        ser = df.reset_index()[self.__col_feature]

        # R のプログラム
        r_program = """
            ser <- ser[,1]
            
            len_ser <- length(ser)
            mu_sequential_smooth <- numeric(len_ser)
            sigma_sequential_smooth <- numeric(len_ser)

            mod <- dlmModPoly(order=1, m0={m0}, C0={C0}, dW={dW}, dV={dV})

            for (i in 1:len_ser) {{
                state_filter <- dlmFilter(ser[1:i], mod)
                state_smooth <- dlmSmooth(state_filter)

                ix <- i + 1 - {lag}
                if (0 < ix) {{
                    mu_sequential_smooth[i] <- state_smooth$s[ix]  
                    sigma_sequential_smooth[i] <- state_smooth$D.S[ix]
                }} else {{
                    mu_sequential_smooth[i] <-  NA
                    sigma_sequential_smooth[i] <- NA
                }}
            }}

            feature <- data.frame(
                mu_sequential_smooth=mu_sequential_smooth,
                sigma_sequential_smooth=sigma_sequential_smooth)

            if ({can_filter}) {{
                feature['mu_filter'] <- state_filter$m[-1]
                feature['sigma_filter'] <- state_filter$D.R[,1]
            }}

            if ({can_smooth}) {{
                state_smooth <- dlmSmooth(state_filter)
                feature['mu_smooth'] <- state_smooth$s[-1]
                feature['sigma_smooth'] <- state_smooth$D.S[-1]
            }}
            """

        # R のプログラムに変数埋め込み
        r_program = r_program.format(
            m0=self.__m0, C0=self.__C0, dW=self.__dW, dV=self.__dV,
            lag=self.__lag, can_filter=self.__can_filter,
            can_smooth=self.__can_smooth)

        # R プログラムを実行
        self.__r.assign('ser', ser)
        self.__r(r_program)
        feature = self.__r.get('feature')

        # インデックスを設定
        feature.index = df.index
        
        # カラム名の前後の空白を除去
        feature.columns = [col.strip() for col in feature.columns]

        return feature