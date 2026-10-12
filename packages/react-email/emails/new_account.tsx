import { Text } from "@react-email/components"
import { LinkButton } from "../ui/Button"
import { Callout, Detail } from "../ui/Callout"
import { Heading } from "../ui/Heading"
import { Layout } from "../ui/Layout"
import { Link } from "../ui/Link"

type NewAccountProps = {
  project_name: string
  username: string
  password: string
  link: string
}

export default function NewAccount({
  project_name = "{{ project_name }}",
  username = "{{ username }}",
  password = "{{ password }}",
  link = "{{ link }}",
}: NewAccountProps) {
  return (
    <Layout
      title={`${project_name} - Nueva cuenta`}
      preview={`Tu cuenta de ${project_name} está lista`}
      project_name={project_name}
    >
      <Heading>¡Te damos la bienvenida a {project_name}!</Heading>
      <Text style={bodyTextStyle}>Hola:</Text>
      <Text style={bodyTextStyle}>
        Creamos tu cuenta para {username} y ya está lista para usarse. Estas
        son tus credenciales:
      </Text>
      <Callout>
        <Detail label="Usuario" value={username} />
        <Detail label="Contraseña" value={password} />
      </Callout>
      <Text style={bodyTextStyle}>
        Empieza iniciando sesión en tu panel:
      </Text>
      <LinkButton href={link}>Entrar a mi cuenta</LinkButton>
      <Text style={supportingTextStyle}>
        O copia y pega este enlace en tu navegador:
        <br />
        <Link href={link}>{link}</Link>
      </Text>
      <Text style={supportingTextStyle}>
        Por seguridad, cambia tu contraseña después de tu primer inicio de
        sesión.
      </Text>
    </Layout>
  )
}

const bodyTextStyle = {
  color: "#334155",
  fontSize: "15px",
  lineHeight: "26px",
  margin: "0 0 18px",
}

const supportingTextStyle = {
  color: "#64748b",
  fontSize: "14px",
  lineHeight: "23px",
  margin: "0 0 16px",
}
