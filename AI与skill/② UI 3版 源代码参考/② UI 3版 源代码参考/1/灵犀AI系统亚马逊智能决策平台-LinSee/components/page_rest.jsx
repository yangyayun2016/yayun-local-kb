// ==================================================================
//  LinSee · History / Knowledge / Team / Membership
// ==================================================================

window.PageHistory = function PageHistory({ lang }) {
  return (
    <>
      <div className="page-accent" />
      <div className="page-h">
        <div>
          <h1 className="page-title">{lang === "zh" ? <>浏览与诊断 <em>历史</em></> : <>Audit <em>History</em></>}</h1>
          <div className="page-sub">{lang === "zh" ? "你最近 30 天的所有诊断记录与分享链接，可按 ASIN 或成员筛选。" : "Last 30 days of audits and shared links."}</div>
        </div>
        <button className="btn btn-sm"><Icon d={Icons.download} size={12} /> {lang === "zh" ? "导出全部" : "Export all"}</button>
      </div>
      <div className="card">
        <table className="tbl">
          <thead>
            <tr>
              <th style={{ width: 120 }}>{lang === "zh" ? "时间" : "Time"}</th>
              <th>ASIN</th>
              <th>{lang === "zh" ? "触发方式" : "Trigger"}</th>
              <th>{lang === "zh" ? "总分变化" : "Score Δ"}</th>
              <th>{lang === "zh" ? "操作人" : "By"}</th>
              <th>{lang === "zh" ? "分享链接" : "Share"}</th>
            </tr>
          </thead>
          <tbody>
            {[
              { t: "2026-04-16 14:32", a: "B09GTRVJQM", trig: "手动", from: 82, to: 84, by: "MC", who: "Maya Chen" },
              { t: "2026-04-15 20:15", a: "B09GTRVJQM", trig: "对比触发", from: 82, to: 82, by: "MC", who: "Maya Chen" },
              { t: "2026-04-14 09:00", a: "B0B2D77YB8", trig: "每周自动", from: 78, to: 81, by: "系统", who: "System" },
              { t: "2026-04-12 16:48", a: "B08L5WRWNW", trig: "手动", from: 72, to: 72, by: "RW", who: "Ryan Wu" },
              { t: "2026-04-10 11:12", a: "B0CR6V4T8H", trig: "批量导入", from: 0, to: 38, by: "MC", who: "Maya Chen" },
              { t: "2026-04-09 09:00", a: "B09GTRVJQM", trig: "每周自动", from: 79, to: 82, by: "系统", who: "System" },
              { t: "2026-04-08 14:22", a: "B0B2D77YB8", trig: "手动", from: 76, to: 78, by: "LZ", who: "Ling Zhao" },
            ].map((x, i) => (
              <tr key={i}>
                <td className="asin-mono">{x.t}</td>
                <td><span className="asin-mono">{x.a}</span></td>
                <td><span className="tag">{x.trig}</span></td>
                <td>
                  <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                    <GradeBadge score={x.from} />
                    <Icon d={Icons.chevronR} size={10} />
                    <GradeBadge score={x.to} />
                    <span className="asin-mono" style={{ color: x.to - x.from > 0 ? "var(--green)" : x.to - x.from < 0 ? "var(--red)" : "var(--ink-mute)" }}>
                      {x.to - x.from > 0 ? "+" : ""}{x.to - x.from}
                    </span>
                  </div>
                </td>
                <td>
                  <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                    <div className="nav-avatar" style={{ width: 22, height: 22, fontSize: 10 }}>{x.by}</div>
                    <span>{x.who}</span>
                  </div>
                </td>
                <td><button className="btn btn-ghost btn-sm"><Icon d={Icons.copy} size={12} /> {lang === "zh" ? "复制" : "Copy"}</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
};

window.PageKnowledge = function PageKnowledge({ lang }) {
  return (
    <>
      <div className="page-accent" />
      <div className="page-h">
        <div>
          <h1 className="page-title">{lang === "zh" ? <>CDQ <em>知识库</em></> : <>CDQ <em>Knowledge</em></>}</h1>
          <div className="page-sub">{lang === "zh" ? "ASCS 官方规则拆解、高分 Listing 范式、限制词清单与问题溯源。" : "Rule explainers, best-practice patterns, restricted words and troubleshooting."}</div>
        </div>
        <div className="row">
          <div className="seg">
            <button className="active">{lang === "zh" ? "全部" : "All"}</button>
            <button>{lang === "zh" ? "评分规则" : "Rules"}</button>
            <button>{lang === "zh" ? "案例库" : "Cases"}</button>
            <button>{lang === "zh" ? "合规" : "Compliance"}</button>
          </div>
        </div>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16 }}>
        {LS_KB.map((kb, i) => (
          <div key={i} className="kb-tile">
            <div className="kb-cat">{kb.cat}</div>
            <div className="kb-title">{kb.title}</div>
            <div className="kb-excerpt">{kb.excerpt}</div>
            <div className="kb-foot">
              <Icon d={Icons.note} size={12} /> {lang === "zh" ? "阅读约 5 分钟" : "5 min read"}
              <span style={{ marginLeft: "auto" }}>{lang === "zh" ? "已收藏 1.2k" : "1.2k saves"}</span>
            </div>
          </div>
        ))}
      </div>
    </>
  );
};

window.PageTeam = function PageTeam({ lang }) {
  return (
    <>
      <div className="page-accent" />
      <div className="page-h">
        <div>
          <h1 className="page-title">{lang === "zh" ? <>团队 <em>工作台</em></> : <>Team <em>Workspace</em></>}</h1>
          <div className="page-sub">{lang === "zh" ? "查看成员最近动作、未解决的批注与分享链接审批。" : "Members, open annotations, shared-link approvals."}</div>
        </div>
        <button className="btn btn-primary btn-sm"><Icon d={Icons.plus} size={12} /> {lang === "zh" ? "邀请成员" : "Invite"}</button>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 360px", gap: 18 }}>
        <div className="card">
          <div className="card-h"><h3>{lang === "zh" ? "成员" : "Members"}</h3></div>
          <table className="tbl">
            <thead><tr><th>{lang === "zh" ? "成员" : "Member"}</th><th>{lang === "zh" ? "角色" : "Role"}</th><th>{lang === "zh" ? "最近活跃" : "Active"}</th><th>{lang === "zh" ? "本周诊断" : "Audits"}</th><th>{lang === "zh" ? "权限" : "Access"}</th></tr></thead>
            <tbody>
              {LS_TEAM.map((t, i) => (
                <tr key={i}>
                  <td>
                    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                      <div className="nav-avatar" style={{ background: t.color }}>{t.init}</div>
                      <span style={{ fontWeight: 500 }}>{t.name}</span>
                    </div>
                  </td>
                  <td>{t.role}</td>
                  <td className="asin-mono">{[12, 34, 68, 240][i]} min ago</td>
                  <td className="asin-mono">{[12, 5, 2, 3][i]}</td>
                  <td><span className="tag tag-info">{i === 0 ? "Owner" : "Editor"}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="card">
          <div className="card-h"><h3>{lang === "zh" ? "待处理批注" : "Open notes"}</h3></div>
          <div className="card-body">
            {[
              { who: "Ryan Wu", init: "RW", color: "#2f5d5a", asin: "B09GTRVJQM", dim: "标题", txt: "三版备选文案已出，明天一起对齐" },
              { who: "Ling Zhao", init: "LZ", color: "#b08339", asin: "B0B2D77YB8", dim: "变体", txt: "供应链盘点中，等我一下" },
              { who: "Oscar King", init: "OK", color: "#2f4f87", asin: "B08L5WRWNW", dim: "图片", txt: "应用场景图本周五交" },
            ].map((c, i) => (
              <div key={i} className="comment" style={{ marginBottom: 10 }}>
                <div className="comment-avatar" style={{ background: c.color }}>{c.init}</div>
                <div className="comment-body">
                  <div className="comment-meta"><b>{c.who}</b><span className="asin-mono">{c.asin}</span></div>
                  <div className="comment-text"><span className="tag tag-warn" style={{ marginRight: 6 }}>{c.dim}</span>{c.txt}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
};

window.PageMember = function PageMember({ lang }) {
  return (
    <>
      <div className="page-accent" />
      <div className="page-h">
        <div>
          <h1 className="page-title">{lang === "zh" ? <>会员 <em>中心</em></> : <>Membership</>}</h1>
          <div className="page-sub">{lang === "zh" ? "当前方案、用量与升级选项。企业版支持 API 对接与 SSO。" : "Plan, usage and upgrade. Enterprise unlocks API + SSO."}</div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16, marginBottom: 22 }}>
        {[
          { name: "Starter",   price: "Free",    feats: ["10 次 / 月 诊断", "基础 CDQv3 评分", "公开知识库", "单人使用"] },
          { name: "Growth",    price: "$49",     feats: ["500 次 / 月 诊断", "自定义权重与评级", "团队 5 席 + 批注", "API 200k 次 / 月", "分享链接"], featured: true },
          { name: "Enterprise",price: "Contact", feats: ["无限诊断", "多站点并发监控", "SSO / SCIM / 审计日志", "API SLA 99.9%", "专属客户成功经理"] },
        ].map((p, i) => (
          <div key={i} className={`plan ${p.featured ? "featured" : ""}`}>
            <div className="plan-name">{p.name}</div>
            <div className="plan-price">{p.price}<small> / {lang === "zh" ? "月" : "mo"}</small></div>
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {p.feats.map((f, j) => (
                <div key={j} className="plan-feat"><Icon d={Icons.check} size={13} />{f}</div>
              ))}
            </div>
            <button className={`btn ${p.featured ? "btn-accent" : ""}`} style={{ marginTop: 6, justifyContent: "center" }}>
              {p.featured ? (lang === "zh" ? "当前方案 · 管理" : "Manage") : (lang === "zh" ? "升级" : "Upgrade")}
            </button>
          </div>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18 }}>
        <div className="card">
          <div className="card-h"><h3>{lang === "zh" ? "本月用量" : "This month usage"}</h3></div>
          <div className="card-body">
            {[
              { l: "诊断次数", v: 254, m: 500 },
              { l: "API 调用", v: 128400, m: 200000 },
              { l: "分享链接", v: 18, m: 50 },
              { l: "团队席位", v: 4, m: 5 },
            ].map((u, i) => (
              <div key={i} style={{ marginBottom: 14 }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, marginBottom: 5 }}>
                  <span>{u.l}</span>
                  <span className="asin-mono">{u.v.toLocaleString()} / {u.m.toLocaleString()}</span>
                </div>
                <div className="bar"><div className="bar-fill good" style={{ width: `${(u.v / u.m) * 100}%`, background: u.v / u.m > 0.8 ? "var(--gold)" : "var(--accent)" }} /></div>
              </div>
            ))}
          </div>
        </div>
        <div className="card">
          <div className="card-h"><h3>API {lang === "zh" ? "对接" : "access"}</h3></div>
          <div className="card-body">
            <div style={{ fontSize: 12.5, color: "var(--ink-mute)", marginBottom: 8 }}>{lang === "zh" ? "一行代码把 CDQv3 诊断接入你的 ERP 或工单系统。" : "One-liner to pipe CDQv3 into your ERP."}</div>
            <pre style={{ background: "var(--bg-soft)", padding: 12, borderRadius: 6, fontSize: 12, border: "1px solid var(--rule)", overflowX: "auto", margin: 0 }}>
<code style={{ padding: 0, background: "transparent" }}>{`curl https://api.linsee.ai/v1/score \\
  -H "Authorization: Bearer lnsee_live_••••8f2a" \\
  -d '{"asin":"B09GTRVJQM","marketplace":"US"}'`}</code>
            </pre>
            <div style={{ fontSize: 12, marginTop: 10, display: "flex", gap: 8 }}>
              <span className="tag tag-pass">Live</span>
              <span className="muted">SLA 99.9% · p95 &lt; 420ms</span>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};
