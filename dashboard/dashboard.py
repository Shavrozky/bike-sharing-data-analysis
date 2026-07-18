
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded",
)

sns.set_theme(style="whitegrid")


# =========================================================
# CUSTOM STYLE
# =========================================================

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        div[data-testid="stMetric"] {
            background-color: rgba(128, 128, 128, 0.08);
            border: 1px solid rgba(128, 128, 128, 0.20);
            padding: 16px;
            border-radius: 12px;
        }

        .dashboard-description {
            font-size: 1rem;
            line-height: 1.6;
            margin-bottom: 1rem;
        }

        .insight-box {
            background-color: rgba(128, 128, 128, 0.08);
            border-left: 5px solid #888888;
            padding: 16px;
            border-radius: 8px;
            margin-top: 10px;
            margin-bottom: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# DATA LOADING
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

MAIN_DATA_PATH = BASE_DIR / "main_data.csv"


@st.cache_data
def load_data():
    """Memuat dan memisahkan data harian serta per jam."""

    if not MAIN_DATA_PATH.exists():
        raise FileNotFoundError(
            f"File tidak ditemukan: {MAIN_DATA_PATH}"
        )

    main_dataframe = pd.read_csv(
        MAIN_DATA_PATH,
        parse_dates=["dteday"],
        low_memory=False,
    )

    if "data_level" not in main_dataframe.columns:
        raise ValueError(
            "Kolom data_level tidak ditemukan pada main_data.csv"
        )

    hourly_dataframe = main_dataframe.loc[
        main_dataframe["data_level"].eq("hourly")
    ].copy()

    daily_dataframe = main_dataframe.loc[
        main_dataframe["data_level"].eq("daily")
    ].copy()

    hourly_dataframe["hr"] = pd.to_numeric(
        hourly_dataframe["hr"],
        errors="coerce",
    ).astype("Int64")

    numeric_columns = [
        "casual",
        "registered",
        "cnt",
        "temp_c",
        "humidity_pct",
        "windspeed_kmh",
    ]

    for dataframe in [
        hourly_dataframe,
        daily_dataframe,
    ]:
        for column in numeric_columns:
            if column in dataframe.columns:
                dataframe[column] = pd.to_numeric(
                    dataframe[column],
                    errors="coerce",
                )

    if hourly_dataframe.empty:
        raise ValueError(
            "Data hourly tidak ditemukan dalam main_data.csv"
        )

    if daily_dataframe.empty:
        raise ValueError(
            "Data daily tidak ditemukan dalam main_data.csv"
        )

    return hourly_dataframe, daily_dataframe


try:
    hour_df, day_df = load_data()
except Exception as error:
    st.error(f"Gagal memuat dataset: {error}")
    st.stop()


# =========================================================
# DATA VALIDATION
# =========================================================

required_hour_columns = {
    "dteday",
    "hr",
    "day_type",
    "weather_label",
    "casual",
    "registered",
    "cnt",
}

required_day_columns = {
    "dteday",
    "day_type",
    "weather_label",
    "casual",
    "registered",
    "cnt",
    "temp_c",
    "humidity_pct",
    "windspeed_kmh",
}

missing_hour_columns = required_hour_columns.difference(
    hour_df.columns
)

missing_day_columns = required_day_columns.difference(
    day_df.columns
)

if missing_hour_columns:
    st.error(
        "Kolom berikut tidak ditemukan pada main_data.csv: "
        + ", ".join(sorted(missing_hour_columns))
    )
    st.stop()

if missing_day_columns:
    st.error(
        "Kolom berikut tidak ditemukan pada day_data.csv: "
        + ", ".join(sorted(missing_day_columns))
    )
    st.stop()


# Membuat demand level apabila belum tersedia
if "demand_level" not in day_df.columns:
    demand_labels = [
        "Low",
        "Medium",
        "High",
        "Very High",
    ]

    day_df["demand_level"] = pd.qcut(
        day_df["cnt"],
        q=4,
        labels=demand_labels,
    )


# =========================================================
# HEADER
# =========================================================

st.title("🚲 Bike Sharing Data Analysis Dashboard")

st.markdown(
    """
    <div class="dashboard-description">
        Dashboard ini menampilkan pola penyewaan sepeda pada
        Capital Bikeshare selama periode 2011–2012.
        Analisis difokuskan pada perbedaan jam sibuk antara hari
        kerja dan non-hari kerja serta hubungan kondisi cuaca
        dengan jumlah penyewaan.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SIDEBAR FILTER
# =========================================================

st.sidebar.header("Filter Dashboard")

minimum_date = day_df["dteday"].min().date()
maximum_date = day_df["dteday"].max().date()

selected_dates = st.sidebar.date_input(
    label="Rentang Tanggal",
    value=(minimum_date, maximum_date),
    min_value=minimum_date,
    max_value=maximum_date,
)

if isinstance(selected_dates, (tuple, list)):
    if len(selected_dates) == 2:
        start_date = pd.Timestamp(selected_dates[0])
        end_date = pd.Timestamp(selected_dates[1])
    elif len(selected_dates) == 1:
        start_date = pd.Timestamp(selected_dates[0])
        end_date = pd.Timestamp(selected_dates[0])
    else:
        start_date = pd.Timestamp(minimum_date)
        end_date = pd.Timestamp(maximum_date)
else:
    start_date = pd.Timestamp(selected_dates)
    end_date = pd.Timestamp(selected_dates)


day_type_options = sorted(
    day_df["day_type"].dropna().unique().tolist()
)

selected_day_types = st.sidebar.multiselect(
    label="Jenis Hari",
    options=day_type_options,
    default=day_type_options,
)


weather_options = sorted(
    day_df["weather_label"].dropna().unique().tolist()
)

selected_weather = st.sidebar.multiselect(
    label="Kondisi Cuaca",
    options=weather_options,
    default=weather_options,
)


st.sidebar.markdown("---")

st.sidebar.caption(
    "Gunakan filter untuk melihat perubahan pola penyewaan "
    "berdasarkan tanggal, jenis hari, dan kondisi cuaca."
)


# =========================================================
# APPLY FILTER
# =========================================================

day_filter_mask = (
    day_df["dteday"].between(start_date, end_date)
    & day_df["day_type"].isin(selected_day_types)
    & day_df["weather_label"].isin(selected_weather)
)

hour_filter_mask = (
    hour_df["dteday"].between(start_date, end_date)
    & hour_df["day_type"].isin(selected_day_types)
    & hour_df["weather_label"].isin(selected_weather)
)

filtered_day_df = day_df.loc[day_filter_mask].copy()
filtered_hour_df = hour_df.loc[hour_filter_mask].copy()


if filtered_day_df.empty or filtered_hour_df.empty:
    st.warning(
        "Tidak ada data yang sesuai dengan kombinasi filter. "
        "Silakan ubah rentang tanggal atau pilihan kategori."
    )
    st.stop()


# =========================================================
# SUMMARY METRICS
# =========================================================

total_rentals = int(filtered_day_df["cnt"].sum())

average_daily_rentals = filtered_day_df["cnt"].mean()

total_casual = int(filtered_day_df["casual"].sum())

total_registered = int(filtered_day_df["registered"].sum())

registered_share = (
    total_registered / total_rentals * 100
    if total_rentals > 0
    else 0
)

hourly_average = (
    filtered_hour_df.groupby(
        "hr",
        as_index=False,
    )
    .agg(
        average_rentals=("cnt", "mean")
    )
)

peak_hour_row = hourly_average.loc[
    hourly_average["average_rentals"].idxmax()
]

peak_hour = int(peak_hour_row["hr"])
peak_hour_average = peak_hour_row["average_rentals"]


st.subheader("Ringkasan Penyewaan")

metric_column_1, metric_column_2, metric_column_3, metric_column_4 = (
    st.columns(4)
)

with metric_column_1:
    st.metric(
        label="Total Penyewaan",
        value=f"{total_rentals:,}",
    )

with metric_column_2:
    st.metric(
        label="Rata-Rata Harian",
        value=f"{average_daily_rentals:,.0f}",
    )

with metric_column_3:
    st.metric(
        label="Jam Puncak",
        value=f"{peak_hour:02d}.00",
        delta=f"{peak_hour_average:,.0f} rata-rata/jam",
        delta_color="off",
    )

with metric_column_4:
    st.metric(
        label="Kontribusi Registered",
        value=f"{registered_share:.1f}%",
    )


st.caption(
    f"Data yang ditampilkan mencakup "
    f"{filtered_day_df['dteday'].nunique():,} hari, "
    f"mulai {start_date.strftime('%d %B %Y')} sampai "
    f"{end_date.strftime('%d %B %Y')}."
)


# =========================================================
# DAILY TREND
# =========================================================

st.markdown("---")
st.subheader("Tren Penyewaan Harian")

daily_trend = (
    filtered_day_df.groupby(
        "dteday",
        as_index=False,
    )
    .agg(
        total_rentals=("cnt", "sum")
    )
    .sort_values("dteday")
)

fig, ax = plt.subplots(figsize=(14, 5))

sns.lineplot(
    data=daily_trend,
    x="dteday",
    y="total_rentals",
    ax=ax,
    linewidth=1.8,
)

ax.set_title(
    "Perkembangan Jumlah Penyewaan Sepeda",
    fontsize=14,
    fontweight="bold",
)

ax.set_xlabel("Tanggal")
ax.set_ylabel("Jumlah Penyewaan")
ax.grid(axis="y", alpha=0.3)

fig.tight_layout()

st.pyplot(fig)
plt.close(fig)


# =========================================================
# BUSINESS QUESTION 1
# =========================================================

st.markdown("---")
st.header("Pertanyaan Bisnis 1")

st.markdown(
    """
    **Pada jam berapa rata-rata jumlah penyewaan sepeda mencapai
    nilai tertinggi pada hari kerja dan non-hari kerja?**
    """
)

hourly_pattern = (
    filtered_hour_df.groupby(
        ["day_type", "hr"],
        as_index=False,
    )
    .agg(
        average_total_rentals=("cnt", "mean"),
        average_casual_rentals=("casual", "mean"),
        average_registered_rentals=("registered", "mean"),
    )
)

peak_by_day_type = hourly_pattern.loc[
    hourly_pattern.groupby("day_type")[
        "average_total_rentals"
    ].idxmax()
].copy()


fig, ax = plt.subplots(figsize=(14, 6))

sns.lineplot(
    data=hourly_pattern,
    x="hr",
    y="average_total_rentals",
    hue="day_type",
    marker="o",
    linewidth=2.3,
    ax=ax,
)

for _, peak_row in peak_by_day_type.iterrows():
    ax.scatter(
        peak_row["hr"],
        peak_row["average_total_rentals"],
        s=110,
        zorder=5,
    )

    ax.annotate(
        (
            f'{peak_row["day_type"]}\n'
            f'{int(peak_row["hr"]):02d}.00\n'
            f'{peak_row["average_total_rentals"]:.0f}'
        ),
        xy=(
            peak_row["hr"],
            peak_row["average_total_rentals"],
        ),
        xytext=(0, 18),
        textcoords="offset points",
        ha="center",
        fontweight="bold",
    )

ax.set_title(
    "Rata-Rata Penyewaan Berdasarkan Jam dan Jenis Hari",
    fontsize=14,
    fontweight="bold",
)

ax.set_xlabel("Jam")
ax.set_ylabel("Rata-Rata Jumlah Penyewaan")
ax.set_xticks(range(0, 24))
ax.legend(title="Jenis Hari")
ax.grid(axis="y", alpha=0.3)

fig.tight_layout()

st.pyplot(fig)
plt.close(fig)


peak_insights = []

for _, peak_row in peak_by_day_type.sort_values(
    "day_type"
).iterrows():
    peak_insights.append(
        f"""
        - **{peak_row['day_type']}** mencapai rata-rata penyewaan
          tertinggi pada pukul **{int(peak_row['hr']):02d}.00**
          dengan sekitar
          **{peak_row['average_total_rentals']:,.0f} penyewaan
          per jam**.
        """
    )

st.markdown(
    f"""
    <div class="insight-box">
        <strong>Insight:</strong><br>
        {"".join(peak_insights)}
        Pola jam puncak yang berbeda menunjukkan bahwa pengelola
        perlu menerapkan strategi redistribusi sepeda yang berbeda
        antara hari kerja dan non-hari kerja.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# BUSINESS QUESTION 2
# =========================================================

st.markdown("---")
st.header("Pertanyaan Bisnis 2")

st.markdown(
    """
    **Seberapa besar perbedaan rata-rata penyewaan pada setiap
    kondisi cuaca dan kelompok pengguna mana yang paling sensitif
    terhadap perubahan cuaca?**
    """
)

weather_summary = (
    filtered_day_df.groupby(
        "weather_label",
        as_index=False,
    )
    .agg(
        average_total_rentals=("cnt", "mean"),
        average_casual_rentals=("casual", "mean"),
        average_registered_rentals=("registered", "mean"),
        number_of_days=("cnt", "size"),
    )
    .sort_values(
        "average_total_rentals",
        ascending=False,
    )
)


weather_column_1, weather_column_2 = st.columns(2)


with weather_column_1:
    st.subheader("Total Penyewaan Berdasarkan Cuaca")

    fig, ax = plt.subplots(figsize=(8, 6))

    sns.barplot(
        data=weather_summary,
        x="weather_label",
        y="average_total_rentals",
        ax=ax,
    )

    for container in ax.containers:
        ax.bar_label(
            container,
            fmt="%.0f",
            padding=3,
        )

    ax.set_title(
        "Rata-Rata Penyewaan Harian",
        fontweight="bold",
    )

    ax.set_xlabel("Kondisi Cuaca")
    ax.set_ylabel("Rata-Rata Penyewaan")
    ax.tick_params(
        axis="x",
        rotation=20,
    )
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()

    st.pyplot(fig)
    plt.close(fig)


with weather_column_2:
    st.subheader("Casual dan Registered")

    weather_user_long = weather_summary.melt(
        id_vars="weather_label",
        value_vars=[
            "average_casual_rentals",
            "average_registered_rentals",
        ],
        var_name="user_type",
        value_name="average_rentals",
    )

    weather_user_long["user_type"] = (
        weather_user_long["user_type"].replace(
            {
                "average_casual_rentals": "Casual",
                "average_registered_rentals": "Registered",
            }
        )
    )

    fig, ax = plt.subplots(figsize=(8, 6))

    sns.barplot(
        data=weather_user_long,
        x="weather_label",
        y="average_rentals",
        hue="user_type",
        ax=ax,
    )

    ax.set_title(
        "Rata-Rata Berdasarkan Tipe Pengguna",
        fontweight="bold",
    )

    ax.set_xlabel("Kondisi Cuaca")
    ax.set_ylabel("Rata-Rata Penyewaan")
    ax.tick_params(
        axis="x",
        rotation=20,
    )
    ax.legend(title="Tipe Pengguna")
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()

    st.pyplot(fig)
    plt.close(fig)


if len(weather_summary) > 1:
    best_weather = weather_summary.iloc[0]
    worst_weather = weather_summary.iloc[-1]

    total_decline = (
        1
        - worst_weather["average_total_rentals"]
        / best_weather["average_total_rentals"]
    ) * 100

    casual_decline = (
        1
        - worst_weather["average_casual_rentals"]
        / best_weather["average_casual_rentals"]
    ) * 100

    registered_decline = (
        1
        - worst_weather["average_registered_rentals"]
        / best_weather["average_registered_rentals"]
    ) * 100

    sensitive_user = (
        "casual"
        if casual_decline > registered_decline
        else "registered"
    )

    st.markdown(
        f"""
        <div class="insight-box">
            <strong>Insight:</strong><br>
            Kondisi dengan rata-rata penyewaan tertinggi adalah
            <strong>{best_weather["weather_label"]}</strong>,
            sedangkan kondisi dengan rata-rata terendah adalah
            <strong>{worst_weather["weather_label"]}</strong>.
            Perbedaan rata-rata penyewaan antara kedua kondisi
            tersebut mencapai sekitar
            <strong>{total_decline:.1f}%</strong>.<br><br>

            Pengguna <strong>{sensitive_user}</strong> menjadi
            kelompok yang lebih sensitif terhadap perubahan cuaca.
            Penurunan pengguna casual mencapai sekitar
            <strong>{casual_decline:.1f}%</strong>, sedangkan
            pengguna registered turun sekitar
            <strong>{registered_decline:.1f}%</strong>.
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.info(
        "Pilih lebih dari satu kondisi cuaca untuk membandingkan "
        "besarnya perubahan penyewaan."
    )


# =========================================================
# USER COMPOSITION
# =========================================================

st.markdown("---")
st.subheader("Komposisi Pengguna")

user_composition = pd.DataFrame(
    {
        "user_type": [
            "Casual",
            "Registered",
        ],
        "total_rentals": [
            total_casual,
            total_registered,
        ],
    }
)

user_column_1, user_column_2 = st.columns([1, 1])


with user_column_1:
    fig, ax = plt.subplots(figsize=(7, 5))

    ax.pie(
        user_composition["total_rentals"],
        labels=user_composition["user_type"],
        autopct="%1.1f%%",
        startangle=90,
    )

    ax.set_title(
        "Proporsi Tipe Pengguna",
        fontweight="bold",
    )

    fig.tight_layout()

    st.pyplot(fig)
    plt.close(fig)


with user_column_2:
    st.dataframe(
        user_composition.rename(
            columns={
                "user_type": "Tipe Pengguna",
                "total_rentals": "Total Penyewaan",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )

    st.markdown(
        f"""
        Pengguna registered menyumbang sekitar
        **{registered_share:.1f}%** dari seluruh penyewaan pada
        periode yang dipilih.
        """
    )


# =========================================================
# ADVANCED ANALYSIS
# =========================================================

st.markdown("---")
st.header("Analisis Lanjutan")

st.markdown(
    """
    Segmentasi permintaan menggunakan teknik binning berbasis
    kuartil. Setiap hari dikelompokkan menjadi `Low`, `Medium`,
    `High`, atau `Very High` tanpa menggunakan algoritma
    machine learning.
    """
)

demand_order = [
    "Low",
    "Medium",
    "High",
    "Very High",
]

demand_profile = (
    filtered_day_df.groupby(
        "demand_level",
        observed=False,
        as_index=False,
    )
    .agg(
        number_of_days=("cnt", "size"),
        average_rentals=("cnt", "mean"),
        average_temperature_c=("temp_c", "mean"),
        average_humidity_pct=("humidity_pct", "mean"),
        average_windspeed_kmh=("windspeed_kmh", "mean"),
    )
)

demand_profile["demand_level"] = pd.Categorical(
    demand_profile["demand_level"],
    categories=demand_order,
    ordered=True,
)

demand_profile = demand_profile.sort_values(
    "demand_level"
)


advanced_column_1, advanced_column_2 = st.columns(
    [1.2, 1]
)


with advanced_column_1:
    fig, ax = plt.subplots(figsize=(8, 5))

    sns.barplot(
        data=demand_profile,
        x="demand_level",
        y="average_rentals",
        order=demand_order,
        ax=ax,
    )

    for container in ax.containers:
        ax.bar_label(
            container,
            fmt="%.0f",
            padding=3,
        )

    ax.set_title(
        "Rata-Rata Penyewaan per Tingkat Permintaan",
        fontweight="bold",
    )

    ax.set_xlabel("Tingkat Permintaan")
    ax.set_ylabel("Rata-Rata Penyewaan")
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()

    st.pyplot(fig)
    plt.close(fig)


with advanced_column_2:
    display_demand_profile = demand_profile.copy()

    display_demand_profile = display_demand_profile.rename(
        columns={
            "demand_level": "Tingkat Permintaan",
            "number_of_days": "Jumlah Hari",
            "average_rentals": "Rata-Rata Penyewaan",
            "average_temperature_c": "Suhu Rata-Rata",
            "average_humidity_pct": "Kelembapan Rata-Rata",
            "average_windspeed_kmh": "Angin Rata-Rata",
        }
    )

    st.dataframe(
        display_demand_profile.round(2),
        hide_index=True,
        use_container_width=True,
    )


# =========================================================
# RECOMMENDATION
# =========================================================

st.markdown("---")
st.header("Conclusion & Recommendation")

st.markdown(
    """
    **Rekomendasi Action Item:**

    1. Pengelola perlu menyiapkan sepeda dan kapasitas docking
       station sebelum jam sibuk hari kerja.

    2. Pada non-hari kerja, ketersediaan sepeda perlu difokuskan
       dari siang hingga sore.

    3. Prakiraan cuaca sebaiknya digunakan dalam perencanaan
       redistribusi sepeda harian.

    4. Saat cuaca buruk diperkirakan terjadi, redistribusi ke
       lokasi wisata atau rekreasi dapat dikurangi karena pengguna
       casual lebih sensitif terhadap cuaca.

    5. Kapasitas minimum tetap perlu dipertahankan pada area
       komuter karena pengguna registered memiliki pola penggunaan
       yang lebih stabil.

    6. Segmentasi tingkat permintaan dapat digunakan untuk
       menentukan kebutuhan armada dan petugas operasional.
    """
)


# =========================================================
# DOWNLOAD FILTERED DATA
# =========================================================

st.markdown("---")
st.subheader("Unduh Data")

download_column_1, download_column_2 = st.columns(2)

with download_column_1:
    st.download_button(
        label="Unduh Data Harian",
        data=filtered_day_df.to_csv(index=False).encode("utf-8"),
        file_name="filtered_day_data.csv",
        mime="text/csv",
        use_container_width=True,
    )

with download_column_2:
    st.download_button(
        label="Unduh Data Per Jam",
        data=filtered_hour_df.to_csv(index=False).encode("utf-8"),
        file_name="filtered_hour_data.csv",
        mime="text/csv",
        use_container_width=True,
    )


st.markdown("---")

st.caption(
    "Bike Sharing Dashboard | Dataset Capital Bikeshare 2011–2012"
)
