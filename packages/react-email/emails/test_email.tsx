import { Text } from "@react-email/components"
import { Callout, Detail } from "../ui/Callout"
import { Heading } from "../ui/Heading"
import { Layout } from "../ui/Layout"

type TestEmailProps = {
  project_name: string
  email: string
}

export default function TestEmail({
  project_name = "{{ project_name }}",
  email = "{{ email }}",
}: TestEmailProps) {
  return (
    <Layout
      title={`${project_name} - Correo de prueba`}
      preview={`El envío de correos de ${project_name} funciona`}
      project_name={project_name}
    >
      <Heading>Correo de prueba</Heading>
      <Text style={bodyTextStyle}>Hola:</Text>
      <Text style={bodyTextStyle}>
        Este es un correo de prueba de {project_name}. Si lo estás leyendo, el
        envío de correos está configurado correctamente.
      </Text>
      <Callout>
        <Detail label="Enviado a" value={email} />
      </Callout>
      <Text style={supportingTextStyle}>
        Si no esperabas este correo, puedes ignorarlo con tranquilidad.
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
