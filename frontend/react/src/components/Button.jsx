import React from "react";

// Componente de botão reutilizável.
// Props:
// - className: classes CSS adicionais
// - children: conteúdo do botão
// - ...props: demais props do elemento button
const Button = ({ className = "", children, ...props }) => (
  <button className={`btn ${className}`.trim()} {...props}>
    {children}
  </button>
);

export default Button;
