import { ExperienceList, ShareExperience } from "./Experiences.jsx";
import PetitionForm from "./PetitionForm.jsx";

const STATUS_CLASS = {
  açık: "ok",
  "son gün bugün": "warn",
  geçti: "late",
  "henüz başlamadı": "info",
};

function formatRange(e) {
  return e.date_text;
}

function Deadline({ deadline }) {
  return (
    <section className={`card deadline ${STATUS_CLASS[deadline.status] || ""}`}>
      <h3>Son başvuru günü</h3>
      <p className="big">{deadline.last_day_text}</p>
      <p className="status">
        {deadline.status === "açık" && `${deadline.workdays_left} iş günü kaldı`}
        {deadline.status === "son gün bugün" && "Son gün bugün!"}
        {deadline.status === "geçti" && "Süre geçmiş görünüyor"}
        {deadline.status === "henüz başlamadı" && `Başvuru dönemi ${deadline.window_start_text} günü başlıyor`}
      </p>
      <p className="muted">{deadline.explanation}</p>
    </section>
  );
}

function Sources({ sources }) {
  if (!sources?.length) return null;
  return (
    <section className="card">
      <h3>Yönetmelikteki ilgili maddeler</h3>
      {sources.map((s, i) => (
        <details key={`${s.file}-${s.label}`} open={i === 0} className="source">
          <summary>
            <span className="code">{s.code}</span> {s.label}
            <span className="doc">{s.title}</span>
          </summary>
          <p>{s.text}</p>
        </details>
      ))}
    </section>
  );
}

export default function AnswerCard({ data }) {
  if (!data.topic) {
    return (
      <div className="bubble assistant unknown">
        <p>{data.answer}</p>
      </div>
    );
  }
  return (
    <div className="bubble assistant">
      <div className="topic-line">
        <span className="badge">{data.topic.name}</span>
        <span className="level">{data.topic.level === "tam" ? "Tam destek" : "Bilgi desteği"}</span>
      </div>
      <p className="answer">{data.answer}</p>

      {data.deadline && <Deadline deadline={data.deadline} />}

      {data.required_documents?.length > 0 && (
        <section className="card">
          <h3>Gerekli belgeler</h3>
          <ul>
            {data.required_documents.map((d) => (
              <li key={d}>{d}</li>
            ))}
          </ul>
          {data.office && (
            <p>
              <strong>Başvuru yeri:</strong> {data.office}
            </p>
          )}
        </section>
      )}

      {data.petition_available && <PetitionForm data={data} />}

      {(data.notes?.length > 0 || data.related?.length > 0) && (
        <section className="card notice">
          <h3>Dikkat</h3>
          {data.notes?.map((n) => (
            <p key={n}>{n}</p>
          ))}
          {data.related?.map((r) => (
            <p key={r.note}>
              {r.note}{" "}
              <span className="muted">
                ({r.source.title}, {r.source.label.split(" –")[0]})
              </span>
            </p>
          ))}
        </section>
      )}

      {data.calendar?.length > 0 && (
        <section className="card">
          <h3>Akademik takvimde yaklaşan tarihler</h3>
          <ul>
            {data.calendar.map((e) => (
              <li key={e.event + e.start}>
                <strong>{formatRange(e)}:</strong> {e.event}
              </li>
            ))}
          </ul>
        </section>
      )}

      <Sources sources={data.sources} />
      <ExperienceList items={data.experiences || []} />
      <ShareExperience topic={data.topic} />

      <p className="disclaimer">{data.disclaimer}</p>
    </div>
  );
}
