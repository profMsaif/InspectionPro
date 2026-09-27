import { Link } from "react-router-dom";

type WorkflowStep = {
  step: string;
  title: string;
  description: string;
  to: string;
  ctaLabel: string;
};

type WorkflowGuideProps = {
  title: string;
  intro: string;
  steps: WorkflowStep[];
};

export function WorkflowGuide({ title, intro, steps }: WorkflowGuideProps) {
  return (
    <article className="page-card glass-card">
      <h3 className="section-title">{title}</h3>
      <p className="muted">{intro}</p>
      <div className="workflow-list">
        {steps.map((item) => (
          <div key={item.step} className="workflow-item">
            <div className="workflow-step">{item.step}</div>
            <div>
              <strong>{item.title}</strong>
              <p className="muted workflow-text">{item.description}</p>
            </div>
            <Link className="button" to={item.to}>
              {item.ctaLabel}
            </Link>
          </div>
        ))}
      </div>
    </article>
  );
}

