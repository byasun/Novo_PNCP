import React from "react";

const Footer = ({ className = "", children, ...props }) => (
  <footer className={`footer ${className}`.trim()} {...props}>
    {children}
  </footer>
);

export default Footer;
