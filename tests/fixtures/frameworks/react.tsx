export function CardGrid({ items }: { items: Array<{ id: string; title: string }> }) {
  return (
    <section aria-labelledby="cards-title" className="cards">
      <h2 id="cards-title">Cards</h2>
      {items.map((item) => <article key={item.id}>{item.title}</article>)}
    </section>
  );
}
