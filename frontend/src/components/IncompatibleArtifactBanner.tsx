type Props = {
  message: string;
};

export function IncompatibleArtifactBanner({ message }: Props) {
  return (
    <div class="incompatible-artifact-banner" role="alert">
      <span>Incompatible artifact: {message}</span>
    </div>
  );
}
