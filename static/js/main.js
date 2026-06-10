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
