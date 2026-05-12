import streamlit as st
import pandas as pd
from core.stitch import db
import plotly.express as px
from core.constants import UIConstants
from data.read_repository import (
    get_dashboard_metrics, get_live_queue, get_bed_status_heatmap, 
    get_all_staff, get_system_health, get_analytics_data,
    get_discharge_history, get_triage_options, get_arrival_types,
    get_discharge_types, get_audit_logs, get_staff_by_role,
    get_all_patients_lookup, get_all_active_cases,
    get_wait_time_trends, get_system_alerts, get_patient_flow_stats,
    get_shift_heatmap_data, get_hasta_id_by_tc, get_hasta_id_by_name,
    get_bed_status_detailed, get_live_patient_queue
)
from data.write_repository import (
    update_bed_status_manual, create_staff, archive_staff, record_discharge, 
    update_patient_state, create_patient_admission, create_patient
)
from services.auth_service import AuthService
from services.shift_service import ShiftService
from services.assignment_service import AssignmentService
from services.ui_stabilizer import UIStabilizer

from ui.components.metrics import render_system_health, render_kpi_row
from ui.components.tables import render_advanced_table
from ui.components.bed_cards import render_compact_bed_grid
from ui.components.analytics_panels import (
    render_wait_time_chart, render_triage_distribution_chart, 
    render_patient_flow_summary, render_system_log,
    render_shift_intensity_heatmap, render_patient_flow_chart
)
from ui.components.timeline import render_timeline
from datetime import datetime

def render_staff_dashboard():
    # 🧱 Initialize UI Stabilizer
    UIStabilizer.initialize()
    
    role = st.session_state.role
    user = st.session_state.user
    
    with st.sidebar:
        st.markdown(f"""
            <div style='text-align: center; padding: 15px 0; background: #f8fafc; border-radius: 10px; margin-bottom: 15px; border: 1px solid #e2e8f0;'>
                <div style='font-size: 2.5rem;'>🏥</div>
                <h4 style='margin:5px 0; color:#1e3a5f; font-size:1rem;'>{user.get('Ad', 'Personel')} {user.get('Soyad', 'Girişi')}</h4>
                <span style='background:#dbeafe; color:#1e40af; padding:2px 10px; border-radius:15px; font-size:0.7rem; font-weight:700;'>{role.upper()}</span>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        menu_items = {
            "🏠 Anasayfa": render_prof_dashboard,
            "📝 Hasta Kayıt": render_patient_registration,
            "🚑 Hasta Kuyruğu": render_prof_queue,
            "🛏️ Yatak Yönetimi": render_prof_beds,
            "🚀 Komuta Merkezi": render_operasyon_merkezi,
            "🚪 Çıkış İşlemleri": render_prof_discharge,
            "⚙️ Sistem": render_advanced_system
        }
        
        visible_menu = ["🏠 Anasayfa"]
        if role in ['Admin', 'Kayıt Personeli']: visible_menu += ["📝 Hasta Kayıt"]
        if role in ['Admin', 'Doktor', 'Hemşire']: visible_menu += ["🚑 Hasta Kuyruğu", "🛏️ Yatak Yönetimi"]
        if role in ['Admin', 'Kayıt Personeli', 'Doktor', 'Hemşire']: visible_menu += ["🚀 Komuta Merkezi"]
        if role in ['Admin', 'Hemşire']: visible_menu += ["🚪 Çıkış İşlemleri"]
        if role == 'Admin': visible_menu += ["⚙️ Sistem"]
        
        selection = st.radio("MENÜ", visible_menu, label_visibility="collapsed")
        
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        if st.button("🚪 Güvenli Çıkış", use_container_width=True):
            AuthService.logout()

    menu_items[selection]()

def render_prof_dashboard():
    # 🚨 1. Alert System (Top)
    alerts = get_system_alerts()
    for alert in alerts:
        if alert['type'] == 'warning': st.warning(alert['msg'])
        elif alert['type'] == 'error': st.error(alert['msg'])

    # 🏥 2. Operation Header
    st.markdown(f"""
        <div style='background: #1e3a5f; padding: 15px; border-radius: 8px; color: white; margin-bottom: 15px;'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div style='font-size:1.1rem; font-weight:700; letter-spacing:0.5px;'>🏥 ACİL SERVİS OPERASYON MERKEZİ</div>
                <div style='text-align:right;'>
                    <div style='font-size:0.9rem; font-weight:600;'>{datetime.now().strftime('%H:%M')}</div>
                    <div style='font-size:0.7rem; opacity:0.8;'>{datetime.now().strftime('%d %B %Y')}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # 📊 3. KPI Strip (5-7 Metrics)
    metrics = get_dashboard_metrics()
    render_kpi_row(metrics)

    st.markdown("<br>", unsafe_allow_html=True)

    # 🔄 4. Live Flow Summary (Real Data)
    render_patient_flow_summary(get_patient_flow_stats())
    
    st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)

    # 📐 5. Main Layout (Left: Queue, Right: Analysis)
    col_left, col_right = st.columns([1.5, 1])
    
    with col_left:
        # 🚨 HIGH PRIORITY: Critical Intervention Panel
        critical_queue = get_live_queue()
        if not critical_queue.empty and 'OncelikDurumu' in critical_queue.columns:
            critical_queue = critical_queue[critical_queue['OncelikDurumu'] == 'Kırmızı']
            if not critical_queue.empty:
                st.markdown("<div class='premium-card' style='padding:15px; border: 2px solid #ef4444; background: #fff1f2;'>", unsafe_allow_html=True)
                st.markdown("<span style='font-size:0.9rem; font-weight:800; color:#ef4444;'>🚨 ACİL MÜDAHALE BEKLEYEN KRİTİK VAKALAR</span>", unsafe_allow_html=True)
                st.dataframe(critical_queue[['Hasta', 'Yas', 'Sikayet', 'Bekleme Süresi']], use_container_width=True, hide_index=True)
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)

        st.markdown("<div class='premium-card' style='padding:15px;'>", unsafe_allow_html=True)
        render_advanced_table(get_live_queue(), "Aktif Vaka Kuyruğu", "Anasayfa_Kuyruk", hide_columns=['BasvuruID', 'AtamaID', 'PersonelID', 'Durum', 'GelisSekli', 'GelisZamani', 'WaitTimeMinutes'])
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='premium-card' style='padding:15px;'>", unsafe_allow_html=True)
        st.markdown("<div style='display:flex; justify-content:space-between; align-items:center;'><span style='font-size:0.8rem; font-weight:700; color:#475569;'>🛏️ YATAK PANOSU</span><span style='font-size:0.6rem; color:#64748b;'>CANLI</span></div>", unsafe_allow_html=True)
        df_beds = get_bed_status_heatmap()
        render_compact_bed_grid(df_beds, interactive=False)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='premium-card' style='padding:15px;'>", unsafe_allow_html=True)
        st.markdown("<span style='font-size:0.8rem; font-weight:700; color:#475569;'>📊 ANALİTİK GÖRÜNÜM</span>", unsafe_allow_html=True)
        
        analytics = get_analytics_data()
        
        with st.expander("📈 Günlük Akış Detayları", expanded=False):
            render_patient_flow_chart(analytics['daily'])
            render_advanced_table(analytics['daily'], "Hasta Akışı Verisi", "Analytics_Daily")
            
        with st.expander("📊 Triyaj Dağılım Tablosu", expanded=False):
            render_triage_distribution_chart(analytics['triage'])
            render_advanced_table(analytics['triage'], "Triyaj İstatistikleri", "Analytics_Triage")
            
        with st.expander("🕒 Yoğunluk & Bekleme Analizi", expanded=False):
            render_shift_intensity_heatmap(get_shift_heatmap_data())
            render_wait_time_chart(get_wait_time_trends())
            
        with st.expander("📜 Sistem Denetim Logları", expanded=True):
            render_system_log(get_audit_logs())
            render_advanced_table(get_audit_logs(), "Denetim Kayıtları", "Analytics_Audit")
        st.markdown("</div>", unsafe_allow_html=True)
        
def render_patient_registration():
    st.markdown("<div style='font-size:1.1rem; font-weight:700; color:#1D2D50; margin-bottom:10px;'>📝 HASTA KAYIT VE TRİYAJ MERKEZİ</div>", unsafe_allow_html=True)
    
    with st.form("full_patient_reg"):
        st.markdown("<div class='premium-card' style='padding:15px; border-top:3px solid #3b82f6;'>", unsafe_allow_html=True)
        st.markdown("<span style='font-size:0.8rem; font-weight:700; color:#475569;'>👤 KİMLİK VE BAŞVURU BİLGİLERİ</span>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        ad = c1.text_input("Ad")
        soyad = c2.text_input("Soyad")
        tc = c1.text_input("TC Kimlik No", max_chars=11)
        yas = c2.number_input("Yaş", 0, 120, 30)
        cinsiyet = c1.selectbox("Cinsiyet", ["E", "K"])
        kan = c2.selectbox("Kan Grubu", ["A+", "A-", "B+", "B-", "AB+", "AB-", "0+", "0-"])
        
        st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
        st.markdown("<span style='font-size:0.8rem; font-weight:700; color:#475569;'>🚑 TRİYAJ VE ATAMA</span>", unsafe_allow_html=True)
        
        c3, c4 = st.columns(2)
        sikayet = c3.text_area("Şikayet", height=70)
        arrival_opts = get_arrival_types()
        triage_opts = get_triage_options()
        
        c5, c6 = st.columns(2)
        triyaj_idx = c5.selectbox("Triyaj Seviyesi", triage_opts.index, format_func=lambda x: triage_opts.loc[x, 'SeviyeAdi'])
        gelis_idx = c6.selectbox("Geliş Şekli", arrival_opts.index, format_func=lambda x: arrival_opts.loc[x, 'GelisSekli'])
        gelis = arrival_opts.loc[gelis_idx, 'GelisSekli']
        
        # Displaying System Managed Columns (Read-only Info)
        st.info("ℹ️ `AtamaID`, `BasvuruID` ve `AtamaZamani` SQL Server tarafından otomatik yönetilmektedir.")
        
        if st.form_submit_button("💾 KAYDI VE KUYRUĞA AL", type="primary", use_container_width=True):
            if ad and soyad and tc:
                from data.write_repository import create_patient, create_patient_admission, get_hasta_id_by_tc
                # 1. Create Patient
                create_patient(ad, soyad, tc, cinsiyet, yas, kan, user_id=st.session_state.user_id)
                
                # 2. Get the new Patient ID
                h_id = get_hasta_id_by_tc(tc)
                
                if h_id:
                    # 3. Create Admission (Automatically moves to Queue)
                    create_patient_admission(h_id, sikayet, gelis, int(triage_opts.loc[triyaj_idx, 'SeviyeID']), user_id=st.session_state.user_id)
                    UIStabilizer.notify_success(f"Hasta {ad} {soyad} başarıyla kaydedildi ve doğrudan kuyruğa alındı!")
                    UIStabilizer.safe_rerun()
            else:
                st.error("Lütfen tüm zorunlu alanları doldurun.")
        st.markdown("</div>", unsafe_allow_html=True)


def render_operasyon_merkezi():
    st.markdown("<div style='font-size:1.1rem; font-weight:700; color:#1D2D50; margin-bottom:10px;'>🚑 ACİL SERVİS CANLI OPERASYON MERKEZİ</div>", unsafe_allow_html=True)
    
    # --- BÖLÜM 1: PROFESYONEL FİLTRELEME VE DURUM AKIŞI ---
    st.markdown("<div class='premium-card' style='padding:15px; border-top:3px solid #ef4444; margin-bottom:15px;'>", unsafe_allow_html=True)
    
    from data.read_repository import get_professional_queue
    patients_df = get_professional_queue()
    
    if patients_df.empty:
        st.warning("Kuyrukta aktif hasta bulunmamaktadır.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # FİLTRELEME PANELİ
        c_tri, c_gel, c_dur = st.columns(3)
        
        with c_tri:
            tri_f = st.selectbox("Triyaj Önceliği", ["Tümü", "Kırmızı", "Sarı", "Yeşil"], key="f_tri")
        with c_gel:
            gel_f = st.selectbox("Geliş Tipi", ["Tümü", "Ambulans", "Ayaktan"], key="f_gel")
        with c_dur:
            dur_f = st.selectbox("Hasta Durumu", ["Tümü", "Bekliyor", "Aktif Hasta"], key="f_dur")

        # FİLTRELEME MANTIĞI
        if tri_f != "Tümü": patients_df = patients_df[patients_df['AciliyetDerecesi'] == tri_f]
        if gel_f != "Tümü": patients_df = patients_df[patients_df['DurumAdi'] == gel_f]
        if dur_f != "Tümü": patients_df = patients_df[patients_df['Durum'] == dur_f]

        # DURUM İKONLARI VE ROZETLER
        def durum_icon(status):
            if status == "Bekliyor": return "🟡 Bekliyor"
            elif status == "Aktif Hasta": return "🟢 Aktif Hasta"
            return status

        if not patients_df.empty:
            patients_df['DurumGoster'] = patients_df['Durum'].apply(durum_icon)
            
            # Renklendirme Fonksiyonu (Profesyonel Standart)
            def apply_row_style(row):
                color = ""
                if row.AciliyetDerecesi == 'Kırmızı': color = 'background-color: #ffcccc; color: black; font-weight: bold;' # Çok Acil
                elif row.AciliyetDerecesi == 'Sarı': color = 'background-color: #fff3cd; color: black;'  # Orta
                elif row.AciliyetDerecesi == 'Yeşil': color = 'background-color: #d4edda; color: black;' # Stabil
                return [color] * len(row)

            st.markdown(f"**Toplam Bulunan Hasta:** {len(patients_df)}")
            styled_df = patients_df[['KayitID', 'Hasta', 'AciliyetDerecesi', 'DurumAdi', 'DurumGoster', 'Saat']].style.apply(apply_row_style, axis=1)
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
        else:
            st.info("Seçilen filtrelere uygun hasta bulunamadı.")
            
        if st.button("🔄 Listeyi Yenile", key="refresh_queue"):
            UIStabilizer.safe_rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<hr style='margin:20px 0;'>", unsafe_allow_html=True)
    
    # --- BÖLÜM 2: HIZLI HASTA KABUL VE DOKTOR ATAMA ---
    st.markdown("<div class='premium-card' style='padding:10px; margin-bottom:15px; border-top:3px solid #3b82f6;'>", unsafe_allow_html=True)
    st.markdown("<span style='font-size:0.7rem; font-weight:700; color:#64748b; margin-bottom:5px; display:block;'>⚡ ACİL HASTA KABUL VE DOKTOR ATAMA</span>", unsafe_allow_html=True)
    
    with st.container():
        c1, c2, c3, c4, c5 = st.columns([1.5, 1, 1, 1, 1])
        with c1:
            all_patients = get_all_patients_lookup()
            p_idx = st.selectbox("Hasta", all_patients.index, format_func=lambda x: all_patients.loc[x, 'Hasta'], label_visibility="collapsed")
        with c2:
            triage_opts = get_triage_options()
            t_idx = st.selectbox("Triyaj", triage_opts.index, format_func=lambda x: triage_opts.loc[x, 'SeviyeAdi'], label_visibility="collapsed")
        with c3:
            arrival_opts = get_arrival_types()
            a_idx = st.selectbox("Geliş", arrival_opts.index, format_func=lambda x: arrival_opts.loc[x, 'GelisSekli'], label_visibility="collapsed")
        with c4:
            # Smart Doctor Filter: High Priority -> Specialist
            is_critical = triage_opts.loc[t_idx, 'SeviyeAdi'] == 'Kırmızı'
            doc_filter = "Uzman" if is_critical else "Pratisyen"
            from data.read_repository import get_staff_by_role, get_all_staff_lookup
            docs = get_staff_by_role(doc_filter)
            if docs.empty: docs = get_all_staff_lookup() # Fallback
            d_idx = st.selectbox("Doktor", docs.index, format_func=lambda x: f"Dr. {docs.loc[x, 'Personel']}", label_visibility="collapsed")
        with c5:
            if st.button("➕ KAYDET VE ATA", type="primary", use_container_width=True):
                if all_patients.empty or 'HastaID' not in all_patients.columns:
                    st.error("⚠️ HATA: Seçilecek hasta bulunamadı veya veritabanı boş.")
                else:
                    h_id = int(all_patients.loc[p_idx, 'HastaID'])
                a_name = arrival_opts.loc[a_idx, 'GelisSekli']
                d_id = int(docs.loc[d_idx, 'PersonelID'])
                
                # 1. Create Admission
                from data.write_repository import create_patient_admission, assign_staff_to_patient
                create_patient_admission(h_id, "Hızlı Kayıt", a_name, int(triage_opts.loc[t_idx, 'SeviyeID']), user_id=st.session_state.user_id)
                
                # 2. Get the new Admission ID and assign doctor
                b_id = db.fetch_scalar("SELECT TOP 1 BasvuruID FROM dbo.BASVURU WHERE HastaID = ? ORDER BY GelisZamani DESC", (h_id,))
                assign_staff_to_patient(d_id, b_id, user_id=st.session_state.user_id)
                
                st.balloons()
                UIStabilizer.notify_success(f"✅ İŞLEM BAŞARILI: {all_patients.loc[p_idx, 'Hasta']} başarıyla kaydedildi ve Dr. {docs.loc[d_idx, 'Personel']}'e atandı!")
                UIStabilizer.safe_rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    # --- BÖLÜM 3: HASTA ÇAĞIRMA SİSTEMİ (FIFO tabanlı) ---
    st.markdown("<div class='premium-card' style='padding:15px; background:#f8fafc; border-left:4px solid #3b82f6; margin-bottom:20px;'>", unsafe_allow_html=True)
    st.markdown("<span style='font-size:0.8rem; font-weight:700; color:#475569;'>📢 HASTA ÇAĞIRMA PANELİ</span>", unsafe_allow_html=True)
    if st.button("🔔 SIRADAKİ HASTAYI ÇAĞIR", type="primary", use_container_width=True):
        if not df.empty:
            next_p = df.iloc[0]
            st.success(f"Sıradaki Hasta Çağırıldı: **{next_p['Hasta']}**")
            st.balloons()
        else:
            st.warning("Bekleyen hasta bulunmuyor.")
    st.markdown("</div>", unsafe_allow_html=True)

    c_staff, c_queue = st.columns([1, 1.3])
    
    with c_staff:
        st.markdown("#### 👨‍⚕️ DOKTOR MÜDAHALE DURUMU")
        staff_df = get_staff_by_role("Doktor", 15)
        if not staff_df.empty:
            for _, s in staff_df.iterrows():
                is_busy = s['ActivePatients'] > 0
                status_color = "#E74C3C" if is_busy else "#2ECC71"
                status_text = f"{s['ActivePatients']} Hasta Bakıyor" if is_busy else "Müsait"
                st.markdown(f"""
                    <div style='background:white; border:1px solid #e2e8f0; border-radius:8px; padding:10px; margin-bottom:8px; border-left:6px solid {status_color}; shadow: 0 2px 4px rgba(0,0,0,0.05);'>
                        <div style='font-size:0.9rem; font-weight:bold; color:#1e3a5f;'>{s['Personel']}</div>
                        <div style='font-size:0.75rem; color:{status_color}; font-weight:600;'>{status_text}</div>
                        <div style='font-size:0.7rem; color:#64748b;'>{s['UzmanlikAlani']}</div>
                    </div>
                """, unsafe_allow_html=True)
        
    with c_queue:
        st.markdown("<span style='font-size:0.8rem; font-weight:700; color:#475569;'>🚑 MÜDAHALE BEKLEYENLER</span>", unsafe_allow_html=True)
        waiting = get_live_queue()
        if not waiting.empty:
            for _, w in waiting.iterrows():
                t_color = UIConstants.TRIAGE_COLOR_MAP.get(w.get('OncelikDurumu'), "#94a3b8")
                patient_age = w.get('Yas', '??')
                complaint = (w.get('Sikayet') or "Şikayet belirtilmedi")[:40]
                
                st.markdown(f"""
                    <div style='background:white; border:1px solid #e2e8f0; border-radius:6px; padding:10px; margin-bottom:10px; border-left:4px solid {t_color};'>
                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                            <div>
                                <div style='font-weight:700; color:#1e3a5f; font-size:0.9rem;'>{w.get('Hasta', 'Bilinmeyen')} <span style='color:#64748b; font-weight:400; font-size:0.75rem;'>({patient_age}Y)</span></div>
                                <div style='font-size:0.7rem; color:#64748b;'>🕒 {w.get('GelisZamani').strftime('%H:%M') if hasattr(w.get('GelisZamani'), 'strftime') else '--:--'} | {complaint}...</div>
                            </div>
                            <span style='background:{t_color}15; color:{t_color}; padding:2px 6px; border-radius:4px; font-size:0.65rem; font-weight:700;'>{str(w.get('OncelikDurumu', 'BELİRSİZ')).upper()}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Inline Assignment
                docs = get_staff_by_role("Doktor", 10)
                if not docs.empty:
                    c_sel, c_btn = st.columns([2, 1])
                    d_sel = c_sel.selectbox("Atanacak Doktor", docs.index, format_func=lambda x: docs.loc[x, 'Personel'], key=f"ops_assign_{w['BasvuruID']}", label_visibility="collapsed")
                    if c_btn.button("ATAMA", key=f"ops_btn_{w['BasvuruID']}", use_container_width=True, type="secondary"):
                        success, msg = AssignmentService.assign_patient(int(docs.loc[d_sel, 'PersonelID']), w['BasvuruID'], user_id=st.session_state.user_id)
                        if success:
                            UIStabilizer.notify_success(f"Atama Başarılı: {w['Hasta']} -> {docs.loc[d_sel, 'Personel']}")
                            UIStabilizer.safe_rerun()
                        else:
                            st.error(msg)
        else:
            st.info("Kuyrukta bekleyen aktif vaka bulunmamaktadır.")
    st.markdown("</div>", unsafe_allow_html=True)



def render_prof_beds():
    st.markdown("<div style='font-size:1.1rem; font-weight:700; color:#1e3a5f; margin-bottom:10px;'>🛏️ YATAK VE ODA KONTROL MERKEZİ</div>", unsafe_allow_html=True)
    
    # KPIs for Bed Management (Real Data)
    all_beds = get_bed_status_detailed()
    k1, k2, k3 = st.columns(3)
    k1.metric("Toplam Kapasite", len(all_beds))
    k2.metric("Dolu", len(all_beds[all_beds['Durum'] == 'Dolu']) if not all_beds.empty else 0)
    k3.metric("Boş", len(all_beds[all_beds['Durum'] == 'Boş']) if not all_beds.empty else 0)
    
    st.markdown("<div class='premium-card' style='padding:15px;'>", unsafe_allow_html=True)
    
    # Filter Bar (Compact)
    f1, f2, f3 = st.columns([1, 1, 1])
    oda_filter = f1.multiselect("Oda", sorted(all_beds['OdaNo'].unique()) if not all_beds.empty else [], placeholder="Oda...")
    durum_filter = f2.multiselect("Durum", ["Boş", "Dolu", "Kirli"], placeholder="Durum...")
    search_q = f3.text_input("🔍 Ara (Hasta/Oda)")
    
    filtered_beds = all_beds
    if not all_beds.empty:
        if oda_filter: filtered_beds = filtered_beds[filtered_beds['OdaNo'].isin(oda_filter)]
        if durum_filter: filtered_beds = filtered_beds[filtered_beds['Durum'].isin(durum_filter)]
        if search_q: 
            filtered_beds = filtered_beds[
                filtered_beds['Hasta'].str.contains(search_q, case=False, na=False) | 
                filtered_beds['OdaNo'].astype(str).str.contains(search_q, case=False)
            ]

    # Visual Bed Grid (Interactive Cards)
    if filtered_beds.empty:
        st.info("Eşleşen yatak bulunamadı.")
    else:
        grid_cols = st.columns(4)
        for idx, (_, row) in enumerate(filtered_beds.iterrows()):
            with grid_cols[idx % 4]:
                is_dolu = row['Durum'] == 'Dolu'
                color = "#ef4444" if is_dolu else "#10b981"
                bg_color = "#fee2e2" if is_dolu else "#ecfdf5"
                status_text = "DOLU" if is_dolu else "BOŞ"
                patient_info = f"<div style='font-size:0.8rem; color:#475569; margin-top:5px;'>👤 {row['Hasta']}</div>" if row['Hasta'] else ""
                
                st.markdown(f"""
                    <div style='border:2px solid {color}; border-radius:12px; padding:12px; background:{bg_color}; margin-bottom:10px; min-height:120px; box-shadow:0 2px 4px rgba(0,0,0,0.05);'>
                        <div style='font-size:0.7rem; font-weight:700; color:#64748b;'>ODA {row['OdaNo']}</div>
                        <div style='font-size:1.1rem; font-weight:800; color:#1e293b;'>Yatak {row['YatakNo']}</div>
                        <div style='font-weight:700; color:{color}; font-size:0.85rem; margin:5px 0;'>{status_text}</div>
                        {patient_info}
                    </div>
                """, unsafe_allow_html=True)
                
                if is_dolu:
                    if st.button(f"Boşalt ({row['YatakNo']})", key=f"rel_{row['YatakID']}", use_container_width=True):
                        from data.write_repository import release_bed
                        release_bed(row['YatakID'], user_id=st.session_state.user_id)
                        UIStabilizer.notify_success(f"Yatak {row['YatakNo']} boşaltıldı.")
                        UIStabilizer.safe_rerun()
                else:
                    if st.button(f"Hasta Yatır ({row['YatakNo']})", key=f"occ_{row['YatakID']}", type="primary", use_container_width=True):
                        st.session_state.target_bed = row.to_dict()
                        UIStabilizer.safe_rerun()

    # Assignment Logic (Modal-like Expander)
    if st.session_state.get('target_bed'):
        st.markdown("<hr>", unsafe_allow_html=True)
        with st.expander(f"📥 HASTA YATIRMA: Yatak {st.session_state.target_bed['YatakNo']}", expanded=True):
            from data.read_repository import get_live_patient_queue
            queue = get_live_patient_queue()
            if not queue.empty:
                selected_patient_idx = st.selectbox("Yatırılacak Hastayı Seçin", queue.index, format_func=lambda x: f"{queue.loc[x, 'Hasta']} ({queue.loc[x, 'OncelikDurumu']})")
                c1, c2 = st.columns(2)
                if c1.button("Atamayı Tamamla", use_container_width=True, type="primary"):
                    from data.write_repository import assign_patient_to_bed
                    from data.read_repository import db
                    h_id = db.fetch_scalar("SELECT HastaID FROM dbo.BASVURU WHERE BasvuruID = ?", (int(queue.loc[selected_patient_idx, 'BasvuruID']),))
                    assign_patient_to_bed(h_id, st.session_state.target_bed['YatakID'], user_id=st.session_state.user_id)
                    del st.session_state.target_bed
                    UIStabilizer.notify_success("Hasta yatağa başarıyla yatırıldı.")
                    UIStabilizer.safe_rerun()
                if c2.button("İptal", use_container_width=True):
                    del st.session_state.target_bed
                    UIStabilizer.safe_rerun()
            else:
                st.warning("Kuyrukta bekleyen hasta bulunmuyor.")
                if st.button("Kapat"):
                    del st.session_state.target_bed
                    UIStabilizer.safe_rerun()
                    
    st.markdown("</div>", unsafe_allow_html=True)


    # 3. BOTTOM SECTION: TIMELINE (Optional)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.session_state.get('selected_bed'):
        st.markdown("#### 🕒 Hasta İşlem Geçişleri")
        # You could add timeline here if you want



def render_prof_discharge():
    st.markdown("<div style='font-size:1.1rem; font-weight:700; color:#1D2D50; margin-bottom:10px;'>🚪 HASTA TABURCU VE ÇIKIŞ İŞLEMLERİ</div>", unsafe_allow_html=True)
    
    col_main, col_stats = st.columns([1.5, 1])
    
    with col_main:
        # 1. TOP SECTION: ACTIVE PATIENT SELECTION
        st.markdown("<div class='premium-card' style='padding:20px; border-top:3px solid #6366f1;'>", unsafe_allow_html=True)
        st.markdown("<span style='font-size:0.8rem; font-weight:700; color:#475569;'>📤 TABURCU EDİLECEK HASTA SEÇİMİ</span>", unsafe_allow_html=True)
    
    from data.read_repository import get_professional_queue
    all_q = get_professional_queue()
    active_patients = all_q[all_q['Durum'] == 'Aktif Hasta'] if not all_q.empty else pd.DataFrame()
    
    if active_patients.empty:
        st.info("Şu an sistemde taburcu edilecek 'Aktif Hasta' bulunmamaktadır.")
    else:
        active_patients['Display'] = active_patients['KayitID'].astype(str) + " - " + active_patients['Hasta']
        selected_idx = st.selectbox("Tedavisi Tamamlanan Hastayı Seçin", active_patients.index, format_func=lambda x: active_patients.loc[x, 'Display'])
        
        c1, c2 = st.columns(2)
        discharge_type = c1.selectbox("Çıkış Türü", ["Taburcu", "Vefat", "Sevk", "Kendi İsteğiyle"])
        note = c2.text_input("Çıkış Notu (Opsiyonel)")
        
        if st.button("🚪 ÇIKIŞI ONAYLA VE KAYDET", type="primary", use_container_width=True):
            b_id = int(active_patients.loc[selected_idx, 'KayitID'])
            
            # Update BASVURU state
            from core.stitch import db
            db.execute("UPDATE dbo.BASVURU SET Durum = 'Taburcu', CikisTarihi = GETDATE() WHERE BasvuruID = ?", (b_id,))
            
            # Record in CIKIS table
            from data.write_repository import create_patient_discharge
            create_patient_discharge(b_id, discharge_type, note, user_id=st.session_state.user_id)
            
            st.balloons()
            UIStabilizer.notify_success(f"Hasta {active_patients.loc[selected_idx, 'Hasta']} başarıyla taburcu edildi.")
            UIStabilizer.safe_rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    with col_stats:
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        st.markdown("##### 📊 Günlük Taburcu Özeti")
        # Basit bir sayaç veya grafik eklenebilir
        history = get_discharge_history()
        today_count = len(history[pd.to_datetime(history['CikisZamani']).dt.date == datetime.now().date()]) if not history.empty else 0
        
        st.metric("Bugünkü Taburcu", today_count, delta="+2" if today_count > 0 else "0")
        st.caption("Son 24 saat içindeki çıkış operasyonları.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.markdown("##### 🕒 Geçmiş Çıkış Kayıtları (Audit Log)")
    render_advanced_table(get_discharge_history(), "", "Discharge_History_Table")
    st.markdown("</div>", unsafe_allow_html=True)

def render_prof_queue():
    st.markdown("<div style='font-size:1.1rem; font-weight:700; color:#1D2D50; margin-bottom:10px;'>🚑 HASTA KUYRUĞU (OPERASYONEL LİSTE)</div>", unsafe_allow_html=True)
    st.markdown("<div class='premium-card' style='padding:15px;'>", unsafe_allow_html=True)
    
    from data.read_repository import get_professional_queue
    df = get_professional_queue()
    
    if df.empty:
        st.info("Kuyrukta bekleyen aktif hasta bulunmamaktadır.")
    else:
        # Standard table without row styling (colorless)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"ℹ️ Toplam {len(df)} vaka sistemde aktif olarak bekliyor.")
        
        if st.button("🔄 LİSTEYİ YENİLE", key="refresh_prof_queue"):
            UIStabilizer.safe_rerun()
            
    st.markdown("</div>", unsafe_allow_html=True)

def render_advanced_reports():
    st.title("📈 Kurumsal Operasyon Raporları")
    data = get_analytics_data()
    c1, c2 = st.columns(2)
    with c1: st.plotly_chart(px.area(data['daily'], x='Tarih', y='Sayi', title="Saatlik Vaka Grafiği"), use_container_width=True)
    with c2: st.plotly_chart(px.pie(data['triage'], values='Sayi', names='OncelikDurumu', title="Triage Dağılımı", color='OncelikDurumu', color_discrete_map=UIConstants.TRIAGE_COLOR_MAP), use_container_width=True)

def render_advanced_system():
    st.title("⚙️ Sistem Ayarları")
    st.markdown("#### 👨‍⚕️ PERSONEL YÖNETİMİ")
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        with st.expander("➕ YENİ PERSONEL EKLE"):
            with st.form("add_staff_form"):
                s_ad, s_soyad = st.text_input("Adı"), st.text_input("Soyadı")
                s_unvan = st.selectbox("Unvan", ["Doktor", "Hemşire", "Teknisyen"])
                s_uzmanlik = st.text_input("Uzmanlık Alanı")
                s_vardiya = st.selectbox("Vardiya", ["Gündüz", "Gece"])
                st.text_input("Durum", value="Aktif", disabled=True)
                if st.form_submit_button("💾 PERSONELİ KAYDET", use_container_width=True):
                    create_staff(s_ad, s_soyad, s_unvan, s_uzmanlik, s_vardiya)
                    UIStabilizer.safe_rerun()
    with c2:
        with st.expander("📦 PERSONEL ARŞİVLE"):
            df_staff = get_all_staff()
            df_act = df_staff[df_staff['Durum'] == 'Aktif']
            if not df_act.empty:
                s_idx = st.selectbox("Arşivlenecek Personel", df_act.index, format_func=lambda x: f"{df_act.loc[x, 'Ad']} {df_act.loc[x, 'Soyad']}")
                if st.button("🔒 ARŞİVLE", use_container_width=True):
                    archive_staff(df_act.loc[s_idx, 'PersonelID'], user_id=st.session_state.user_id)
                    UIStabilizer.safe_rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📋 Aktif Personel Listesi")
    st.dataframe(get_all_staff(), use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🛡️ GÜVENLİK VE İŞLEM GÜNLÜĞÜ")
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.dataframe(get_audit_logs(), use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    render_system_health(get_system_health())
