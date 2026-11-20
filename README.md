# Day 12 — AI SDLC: Đảo Đèn Lồng

> **Demo Video:** *(Link to `v1.0.0` Release `demo.mp4` or `docs/demo/demo.mp4` will be added in Phase 4)*
> **Cá nhân** (1 người / 1 MSSV) · Áp dụng SDLC cùng AI để xây một **game 3D** qua **4 phase**, từ yêu cầu ban đầu tới bản phát hành.
> **Lab board + trợ giảng:** **[Đảo Đèn Lồng Lab](https://claude.ai/artifact/Q1RYyv1dxjUczzCbd2ZnoW)**

## Quick Start (≤ 3 commands)

Requires **Python >= 3.11** (stdlib only; zero external Python packages required).

```bash
git clone https://github.com/onedvu315itech/K5-L3A-DAY12-VuLeDuc-2A202603683-AI-SDLC-Dao-Den-Long.git
cd K5-L3A-DAY12-VuLeDuc-2A202603683-AI-SDLC-Dao-Den-Long
python3 game/src/play.py   # On Windows if `python3` opens Store stub: `python3.12 game/src/play.py`
```

Then open `http://127.0.0.1:8000` in your browser to play **Đêm 1 – Đảo Bến**.

### Controls (Điều khiển)
- `W A S D` / `↑ ↓`: Di chuyển Mây theo hướng camera
- `Space`: Nhảy (`jump`)
- `Shift`: Lướt (`dash`, `14 m/s` trong `0.2s`, hồi chiêu `1.5s`)
- `Q` / `← →` / Kéo chuột: Xoay góc nhìn camera 3D (`cam_yaw_deg`)
- `E`: Nạp đom đóm để thắp Đèn Lồng Lớn (`interact`, bán kính `2.0m`, cần `10` đom đóm/đèn)
- `F` hoặc `J`: Tỏa Sáng (`pulse`, tốn `3` đom đóm, bán kính `5.0m`, choáng `2.0s` & đẩy lùi `4.0m`, hồi chiêu `3.0s`)
- `Esc` hoặc `P`: Tạm dừng (`pause`)

### Scoring & Tuning (Cách tính điểm & thông số chuẩn — Contract v1.2)
Khai báo chính xác trong [game.contract.json](file:///d:/aithucchien-vinuni/projects/K5-L3A-DAY12-VuLeDuc-2A202603683-AI-SDLC-Dao-Den-Long/game.contract.json):
- **Nạp đom đóm vào đèn (thắp mới / thắp lại / châm dầu):** `+5` điểm / đom đóm nạp (`capacity = min(20, 10 + 2 × successful_lights)`).
- **Thắp đèn lần đầu / Thắp lại:** `+100` lần đầu (`10` đom đóm) · `+40` thắp lại (`5` đom đóm).
- **Châm dầu đèn đang sáng (`fuel < 100`):** `+10` fuel / đom đóm; đèn tự hao `1.0/s` và bị Bóng Mực hút `5/s` khi `fuel < 30`.
- **Tỏa Sáng trúng Bóng Mực (`per_stun`):** `+5` điểm / Bóng Mực (`+15` nếu đang hút dầu `drain`).
- **Thắng khi giữ đảo sáng tới Bình Minh (`dawn_survived`):** Đêm 1/2/3 (`240/270/300s`) cần ≥ `60%` số đèn đang sáng (`3/5`, `4/6`, `5/7`); thưởng `+50 + floor(fuel)` mỗi đèn sáng + `+50` mỗi Ngọn Lửa còn lại.
- **Tài liệu thay đổi Phase 3:** Xem [ADR-001](file:///d:/aithucchien-vinuni/projects/K5-L3A-DAY12-VuLeDuc-2A202603683-AI-SDLC-Dao-Den-Long/game/docs/notes/adr-001-lantern-fuel-dawn.md) và [CHANGELOG.md](file:///d:/aithucchien-vinuni/projects/K5-L3A-DAY12-VuLeDuc-2A202603683-AI-SDLC-Dao-Den-Long/CHANGELOG.md).

### Tests, Headless, Benchmark, Soak & Leaderboard (Test Contract v1.3)
- **System Requirements:** Python `>= 3.11` (stdlib only, zero third-party packages) + modern WebGL browser (Chrome / Edge / Firefox / Safari) on macOS, Linux, or Windows.
- **Run full verification suite (16 unit/contract tests + Nights 1–3 headless determinism):**
  ```bash
  python3 game/scripts/verify.py
  ```
- **Run headless contract CLI (`--night 1 | 2 | 3`):**
  ```bash
  python3 game/src/headless.py --seed 42 --night 3 --ticks 21600 --out out.jsonl --snapshot-every 60
  ```
- **Run 30s Benchmark (`bench.json`):**
  ```bash
  python3 game/src/bench.py --seed 42 --duration 30 --out bench.json
  ```
  *(Note: In browser mode `http://127.0.0.1:8000/?bench=1&seed=42&duration=30`, WebGL `requestAnimationFrame` vsync is managed by the browser/OS unless launched with `--disable-gpu-vsync`; CLI `bench.py` runs uncapped with `vsync_off: true`.)*
- **Run 10-Night Soak Test (`soak.json`):**
  ```bash
  python3 game/src/soak.py --seed 7 --nights 10 --out soak.json
  ```
- **Export Top-10 Local Leaderboard:**
  ```bash
  python3 game/src/play.py --export-leaderboard out.json
  ```
- **Documentation & Proof:**
  - [CHANGELOG.md](file:///d:/aithucchien-vinuni/projects/K5-L3A-DAY12-VuLeDuc-2A202603683-AI-SDLC-Dao-Den-Long/CHANGELOG.md) · [CREDITS.md](file:///d:/aithucchien-vinuni/projects/K5-L3A-DAY12-VuLeDuc-2A202603683-AI-SDLC-Dao-Den-Long/CREDITS.md) · [LICENSE](file:///d:/aithucchien-vinuni/projects/K5-L3A-DAY12-VuLeDuc-2A202603683-AI-SDLC-Dao-Den-Long/LICENSE)
  - [Phase 1–4 Proofs](file:///d:/aithucchien-vinuni/projects/K5-L3A-DAY12-VuLeDuc-2A202603683-AI-SDLC-Dao-Den-Long/game/docs/proof/README.md) · [Assumptions](file:///d:/aithucchien-vinuni/projects/K5-L3A-DAY12-VuLeDuc-2A202603683-AI-SDLC-Dao-Den-Long/game/docs/notes/assumptions.md) · [ADR-001](file:///d:/aithucchien-vinuni/projects/K5-L3A-DAY12-VuLeDuc-2A202603683-AI-SDLC-Dao-Den-Long/game/docs/notes/adr-001-lantern-fuel-dawn.md) · [AI & Token Log](file:///d:/aithucchien-vinuni/projects/K5-L3A-DAY12-VuLeDuc-2A202603683-AI-SDLC-Dao-Den-Long/game/docs/notes/ai-log.md) · [Retrospective](file:///d:/aithucchien-vinuni/projects/K5-L3A-DAY12-VuLeDuc-2A202603683-AI-SDLC-Dao-Den-Long/game/docs/notes/retro.md)

### Sáng tạo của tôi
- **Đèn Hoa Đăng Bến Nước (Shoreline Floating Lotus Lanterns):** Vòng 10 chiếc đèn hoa đăng trôi nhẹ quanh bờ nước Đảo Bến. Mỗi khi Mây thắp sáng thêm 1 Đèn Lồng Lớn, 2 cụm đèn hoa đăng nơi bến nước sẽ tự động bừng sáng ấm áp đồng điệu cùng ánh sáng dần xua tan sương đen trên đảo.
- **Tuân thủ Test Contract:** Hiệu ứng hoa đăng và độ sáng sương mù chỉ nằm ở tầng hiển thị 3D ([game/web/index.html](file:///d:/aithucchien-vinuni/projects/K5-L3A-DAY12-VuLeDuc-2A202603683-AI-SDLC-Dao-Den-Long/game/web/index.html)), hoàn toàn không thêm thực thể hay thay đổi đầu ra JSONL của chế độ headless ([game/docs/proof/phase-1.md](file:///d:/aithucchien-vinuni/projects/K5-L3A-DAY12-VuLeDuc-2A202603683-AI-SDLC-Dao-Den-Long/game/docs/proof/phase-1.md)).

---

## Tài liệu của lab

| File | Nội dung |
|---|---|
| [GUIDE.md](GUIDE.md) | Hướng dẫn làm lab: vòng làm việc mỗi phase, harness, kiểm chứng, token |
| [CHECKPOINTS.md](CHECKPOINTS.md) | Các mốc tự kiểm tra từ chuẩn bị đến nộp bài |
| [SUBMISSION.md](SUBMISSION.md) | Đặt tên repo, hạn nộp, tag, Release, video, checklist |
| [RULES.md](RULES.md) | Quy định: AI, trung thực về bằng chứng, bản quyền, bảo mật |
| [RUBRIC.md](RUBRIC.md) | Thang điểm chi tiết |

## Lab board

Yêu cầu dự án được phát hành tại **[Đảo Đèn Lồng Lab](https://claude.ai/artifact/Q1RYyv1dxjUczzCbd2ZnoW)**. Mỗi phase là một tab (tab chưa phát hành bị khóa), mỗi tab có trợ giảng AI riêng chỉ trả lời trong phạm vi phase đó. Trợ giảng cần đăng nhập claude.ai và dùng lượt Claude của bạn.

## Dự án

**Đảo Đèn Lồng**: game 3D góc nhìn thứ ba. Mây, người giữ đèn nhỏ tuổi, gom đom đóm để thắp lại các Đèn Lồng Lớn và né Bóng Mực trong sương đen.

- Không ràng buộc công nghệ; chạy được trên macOS hoặc Linux.
- Tuân theo **Test Contract** (chế độ headless) để được chấm tự động và so sánh với nhau.

| Phase | Bạn nhận | Nộp |
|---|---|---|
| 1 | **PRD-0** (mô tả tổng quát) + Test Contract | tag `phase-1` |
| 2 | **Ticket-02**, phát hành khi Phase 1 kết thúc | tag `phase-2` |
| 3 | **Ticket-03**, phát hành khi Phase 2 kết thúc | tag `phase-3` |
| 4 | **Ticket-04**, phát hành khi Phase 3 kết thúc | tag `phase-4` + Release `v1.0.0` |

Yêu cầu sẽ được bổ sung và có thể thay đổi giữa các phase, giống dự án thật.

### Lịch 4 giờ

Bài lab kéo dài **4 giờ**. Phase 1 và 2 khoảng **1 giờ**, Phase 3 khoảng **30 phút**, Phase 4 khoảng **1 giờ 30 phút**. Mỗi phase phát hành đúng mốc giờ. Phase mới xuất hiện trên lab board khi tới mốc.

| Mốc | Sự kiện | Hạn tag |
|---|---|---|
| 0h | Phát hành **Phase 1** (PRD-0), gồm cả phần chuẩn bị | `phase-1` trước mốc 1h |
| 1h | Phát hành **Phase 2** | `phase-2` trước mốc 2h |
| 2h | Phát hành **Phase 3** | `phase-3` trước mốc 2h30 |
| 2h30 | Phát hành **Phase 4** | `phase-4`, Release `v1.0.0` và video trước mốc 4h |
| 4h | Hết giờ lab, chốt bài | |

Hết giờ mỗi phase thì tag và chuyển sang phase tiếp theo, dù phase chưa hoàn hảo. Chỗ chưa xong ghi trung thực trong bằng chứng.

---

## Gợi ý SDLC (cách làm là của bạn)

Mỗi phase là một vòng nhỏ. Công cụ, thứ tự, định dạng tài liệu đều tự do; đây chỉ là gợi ý:

1. **Requirements:** biến yêu cầu thành tiêu chí nghiệm thu kiểm chứng được. Chỗ mơ hồ thì tự giả định và ghi lại.
2. **Plan:** nghĩ cách kiểm chứng **trước** khi để agent viết code.
3. **Build:** để agent viết, bạn điều phối và review.
4. **Verify:** chạy thật, kiểm tra hành vi thật. *Không có bằng chứng thì chưa xong*: "agent bảo chạy rồi" không phải bằng chứng.
5. **Evaluate:** cái gì đạt, AI sai ở đâu, harness (AGENTS.md, skill, hook) cần chỉnh gì.
6. **Release:** gắn tag.

## Ba điều cần nhớ

> Bạn được **tự do sáng tạo thêm** quanh phần lõi (nhân vật, cơ chế nhỏ, câu chuyện, hiệu ứng, âm thanh…). Sáng tạo gọn và không phá yêu cầu được tính điểm trong hạng mục F của [RUBRIC](RUBRIC.md); ghi mục "Sáng tạo của tôi" trong README của bạn.

- **Game tốt là game đúng yêu cầu của khách hàng**, không phải game phức tạp hay đẹp nhất. Làm đúng và chứng minh được là đúng trước, trau chuốt sau.
- **Cân nhắc kỹ quota token của bạn.** Đốt nhiều token không làm bài tốt hơn. Ngữ cảnh gọn, kế hoạch rõ, kiểm chứng sớm thường vừa rẻ vừa đúng hơn chạy agent liên tục.
- **Kiểm chứng là phần quan trọng nhất.** Bằng chứng (test, output headless, ảnh, số đo) đáng giá hơn lời mô tả.

---

## Bàn giao cuối cùng

Một **repo GitHub cá nhân, public**, gồm:

1. **Toàn bộ mã nguồn** của game qua 4 phase, tag `phase-1` … `phase-4`, Release `v1.0.0`.
2. **Video demo `.mp4` dưới 5 phút** (đính kèm Release `v1.0.0` hoặc `docs/demo/demo.mp4`, link ở đầu README): chơi thử và cho thấy bằng chứng game chạy đúng.
3. **Bằng chứng kiểm chứng** của từng phase (định dạng tự chọn).
4. **Harness AI đã dùng** (AGENTS.md / CLAUDE.md, skills, hooks, plugins…), giữ nguyên trong repo và lịch sử git.
5. **Ghi chép ngắn:** spec/giả định mỗi phase, nhật ký dùng AI (gồm token/chi phí ước tính), retro.

Không commit API key, token hay `.env`. Gửi link repo theo hướng dẫn của Coach.

## Đánh giá (100 điểm)

| Hạng mục | Điểm |
|---|---|
| Test tự động ẩn (headless, gồm kiểm tra lại phase trước) | 30 |
| Kiểm chứng & bằng chứng của bạn | 20 |
| Quy trình SDLC & harness AI | 15 |
| Evaluation & retro (gồm cách bạn dùng token) | 10 |
| Hiệu năng & ổn định | 10 |
| Chất lượng sản phẩm (đúng yêu cầu, chơi được) | 10 |
| Video demo | 5 |

## Quy định

- Dùng AI thoải mái; không sao chép repo của người khác.
- Bằng chứng phải thật: test luôn đạt hay output sửa tay là vi phạm.
- Nhân vật, bối cảnh là bản gốc của lab; asset bên ngoài chỉ dùng loại CC0/CC-BY/MIT hoặc tự tạo, ghi nguồn trong `CREDITS.md`.
