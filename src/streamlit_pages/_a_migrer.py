# FICHIER TEMPORAIRE, NON EXÉCUTÉ : blocs de 04_02_streamlit_app.py en attente de migration vers leur page.
# Chaque bloc en est retiré au moment où il est déplacé dans streamlit_pages/.


#========================================================================================
# SECTION TESTS
#========================================================================================
if menu == "🪣 Tests" :
    st.markdown("Mon bac à sable 🪣")
    
    
    # Blocs « comptes récemment activés et risque » et « comptes actifs » passés en 4.4 (p4_4_vie_comptes.py).
    # Le bloc suivant utilisait col_graph2, défini avec col_graph1 dans le bloc des comptes actifs.
    col_graph1, col_graph2 = st.columns([1,1])
        
        
    # 6. commentaires sur les 2 graphes
    st.markdown("""
Le nombre de compte présentant un encours (y compris négatif pour les client ayant un trop perçu) augmentent chaque mois. Le nombre de comptes présentant un encours positif (somme à devoir) augmentent également chaque mois. Le taux de clients qui paient tout ou partie de leur échéance est stable sur les 6 mois.  
Cela ne signifie pas que le taux de clients à jour est stable car un client peut présenter un paiement insuffisant pour recouvrer sa dette ou son minimum d'échéance de crédit.
                """)
    st.markdown('---')
    
    
    # Graphe Evolution du taux de clients qui présentent un paiement sur encours positif
    st.markdown("#### Evolution des ratios de paiement moyen et médian par rapport à l'encours de crédit")
    # 1. Appairage chronologique : PAY_AMTn comparé à BILL_AMT(n+1)
    paires_chronologiques = [
        ('PAY_AMT5', 'BILL_AMT6', 'M-5'),
        ('PAY_AMT4', 'BILL_AMT5', 'M-4'),
        ('PAY_AMT3', 'BILL_AMT4', 'M-3'),
        ('PAY_AMT2', 'BILL_AMT3', 'M-2'),
        ('PAY_AMT1', 'BILL_AMT2', 'M-1'),
    ]

    proportions_pct = {}
    counts_dict = {}

    # 2. Calcul du taux de paiement effectif sur encours positif
    for pay_col, bill_col, label in paires_chronologiques:
        if pay_col in df.columns and bill_col in df.columns:
            subset_avec_encours = df[df[bill_col] > 0]

            if len(subset_avec_encours) > 0:
                nb_payeurs = (subset_avec_encours[pay_col] > 0).sum()
                prop = (nb_payeurs / len(subset_avec_encours)) * 100

                proportions_pct[label] = prop
                counts_dict[label] = nb_payeurs

    df_pay = pd.DataFrame({
        'Mois': list(proportions_pct.keys()),
        'Pourcentage': list(proportions_pct.values()),
        'Nombre': list(counts_dict.values()),
    })

    # 3. Création du graphique Plotly
    fig_pay = go.Figure()

    # Barres principales avec le pourcentage au-dessus
    fig_pay.add_trace(
        go.Bar(
            x=df_pay['Mois'],
            y=df_pay['Pourcentage'],
            text=[f'{val:.1f}%' for val in df_pay['Pourcentage']],
            textposition='outside',
            textfont=dict(size=14, color='black'),
            marker_color="#2ca02c", 
            customdata=df_pay['Nombre'],
            hovertemplate=(
                '<b>%{x}</b><br>Payeurs effectifs : %{customdata:,}<br>Taux de'
                ' paiement : %{y:.1f}%<extra></extra>'
            ),
        )
    )

    # Ajout du nombre d'individus à la verticale (n = ...) au centre des barres
    for _, row in df_pay.iterrows():
        fig_pay.add_annotation(
            x=row['Mois'],
            y=row['Pourcentage'] / 2,
            text=f"n = {int(row['Nombre']):,}".replace(',', ' '),
            showarrow=False,
            textangle=-90,  # Texte affiché à la verticale
            font=dict(color='white', size=16, family='Arial Black'),
        )

    # 4. Configuration de la mise en page
    fig_pay.update_layout(
        xaxis_title='Mois',
        yaxis_title='Pourcentage de paiements effectifs (%)',
        yaxis=dict(
            range=[0, 105],
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)',
            gridwidth=1,
        ),
        height=500,
    )

    # 5. Affichage dans Streamlit
    with col_graph2 :
        st.markdown("#### Evolution du taux de clients présentant un paiement sur encours positif")
        st.plotly_chart(fig_pay, width='stretch')
        
        
    # GRAPHES EVOLUTION DES RATIOS DE PAIEMENT SUR DETTE MOYEN ET MEDIAN

    col_graph1, col_graph2 = st.columns([1, 1])

    # 1. Définition des paires de colonnes et des étiquettes de M-5 à M-1
    mapping_ratios = [
        ('ratio_PAY_BILL5', 'M-5'),
        ('ratio_PAY_BILL4', 'M-4'),
        ('ratio_PAY_BILL3', 'M-3'),
        ('ratio_PAY_BILL2', 'M-2'),
        ('ratio_PAY_BILL1', 'M-1'),
    ]

    # Filtrage des colonnes présentes dans le DataFrame
    colonnes_actives = [
        col for col, label in mapping_ratios if col in df.columns
    ]
    labels_x = [label for col, label in mapping_ratios if col in df.columns]

    if len(colonnes_actives) > 0:

    # =========================================================================
    # 1. GRAPHIQUE BLEU : RATIO MOYEN
    # =========================================================================
        moyennes = ratios_affichables(df, colonnes_actives).mean()

        fig_ratio = go.Figure()
        fig_ratio.add_trace(
            go.Scatter(
                x=labels_x,
                y=moyennes.values,
                mode='lines+markers+text',
                text=[f'{val:.2f}' for val in moyennes.values],
                textposition='top center',
                textfont=dict(size=14, color='black'),
                marker=dict(size=9, color='#1f77b4'),  # Bleu
                line=dict(width=2.5, color='#1f77b4'),
                hovertemplate=(
                    '<b>%{x}</b><br>Ratio de paiement moyen :'
                    ' %{y:.2f}%<extra></extra>'
                ),
            )
        )

        max_val_moy = moyennes.max()
        min_val_moy = moyennes.min()
        marge_moy = (
            (max_val_moy - min_val_moy) * 0.25 if max_val_moy != min_val_moy else 0.05
        )

        fig_ratio.update_layout(
            title=dict(
                text=(
                    '<b>Évolution du ratio moyen (Paiement / Facture'
                    ' précédente)</b>'
                ),
                font=dict(size=14),
            ),
            xaxis_title='Mois (Période relative)',
            yaxis_title='Ratio de paiement moyen (%)',
            yaxis=dict(
                range=[min_val_moy - marge_moy, max_val_moy + marge_moy],
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)',
                gridwidth=1,
            ),
            height=500,
        )

        with col_graph1:
            st.plotly_chart(fig_ratio, width='stretch')

        # =========================================================================
        # 2. GRAPHIQUE VIOLET : RATIO MÉDIAN
        # =========================================================================
        medianes = ratios_affichables(df, colonnes_actives).median()

        fig_medianes = go.Figure()
        fig_medianes.add_trace(
            go.Scatter(
                x=labels_x,
                y=medianes.values,
                mode='lines+markers+text',
                text=[f'{val:.2f}' for val in medianes.values],
                textposition='top center',
                textfont=dict(size=14, color='black'),
                marker=dict(size=9, color='#8e44ad'),  # Violet
                line=dict(width=2.5, color='#8e44ad'),
                hovertemplate=(
                    '<b>%{x}</b><br>Ratio de paiement médian :'
                    ' %{y:.2f}%<extra></extra>'
                ),
            )
        )

        max_val_med = medianes.max()
        min_val_med = medianes.min()
        marge_med = (
            (max_val_med - min_val_med) * 0.25 if max_val_med != min_val_med else 0.05
        )

        fig_medianes.update_layout(
            title=dict(
                text=(
                    '<b>Évolution du ratio médian (Paiement / Facture'
                    ' précédente)</b>'
                ),
                font=dict(size=14),
            ),
            xaxis_title='Mois',
            yaxis_title='Ratio de paiement médian (%)',
            yaxis=dict(
                range=[min_val_med - marge_med, max_val_med + marge_med],
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)',
                gridwidth=1,
            ),
            height=500,
        )

        with col_graph2:
            st.plotly_chart(fig_medianes, width='stretch')

    else:
        st.warning("Aucune des colonnes de ratios n'a été trouvée dans le dataset.")
