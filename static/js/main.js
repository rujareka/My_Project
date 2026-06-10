/**
 * IdolAlive Statistics - 기본 JS 뼈대
 */

// 삭제 확인 (덱 삭제 등에서 사용)
document.querySelectorAll('[data-confirm]').forEach(el => {
  el.addEventListener('click', e => {
    if (!confirm(el.dataset.confirm)) e.preventDefault();
  });
});

// 아이돌 필터 (카드/대전기록 페이지)
// 폼 제출 없이 즉시 URL 이동
document.querySelectorAll('.idol-filter-btn').forEach(btn => {
  btn.addEventListener('click', e => {
    e.preventDefault();
    const url = new URL(window.location);
    const idol = btn.dataset.idol || '';
    if (idol) url.searchParams.set('idol', idol);
    else url.searchParams.delete('idol');
    window.location = url.toString();
  });
});

/*
  아이돌 퍼스널 컬러 매핑
  idol_id → 색상코드
  스크린샷 테두리 색상 기반으로 설정, 실제 퍼스널 컬러에 맞게 수정 가능
*/
const IDOL_COLORS = {
  'idol_01': '#e85c6e',  /* 아이자와 히요리  — 레드 */
  'idol_02': '#d4943c',  /* 시노다 사키      — 골드 */
  'idol_03': '#9b5fc0',  /* 히메노 에리      — 퍼플 */
  'idol_04': '#3a9bd4',  /* 루리카와 오토하  — 블루 */
  'idol_05': '#7aab3e',  /* 히이라기 료코    — 그린 */
  'idol_06': '#4db8a8',  /* 코즈키 후미노    — 틸 */
  'idol_07': '#e8709a',  /* 시노미아 쥬리    — 핑크 */
  'idol_08': '#c8a84b',  /* 타카나시 츠카사  — 옐로우골드 */
  'idol_09': '#5b8de8',  /* 아마우 카논      — 로얄블루 */
};

/* 아이돌 칩에 퍼스널 컬러 CSS 변수 주입 */
document.querySelectorAll('.fchip[data-filter="idol"][data-val]').forEach(btn => {
  const idolId = btn.dataset.val;
  if (idolId && IDOL_COLORS[idolId]) {
    btn.style.setProperty('--idol-color', IDOL_COLORS[idolId]);
  }
});
